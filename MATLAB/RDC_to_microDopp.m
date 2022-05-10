function [] = RDC_to_microDopp( RDC, fOut, cfar_bins )
        
        SweepTime = 40e-3; % Time for 1 frame
        numTX = 3; % '1' for 1 TX, '2' for BPM
        NoC = 88;%128; % Number of chirp loops
        NPpF = numTX*NoC; % Number of pulses per frame
        
        % NoF = fileSize/2/NPpF/numRX/NTS; % Number of frames
        numChirps = size(RDC,2);
        NoF = round(numChirps/NPpF); % Number of frames, 4 channels, I&Q channels (2)
        dT = SweepTime/(NPpF/numTX); %
        prf = 1/dT; %
        
        rp = fft(RDC);
        
      %% MTI Filter (not working)
      
%         [m,n]=size(rp(:,:,1));
%         %     ns = size(rp,2)+4;
%         h=[1 -2 3 -2 1]';
%         ns = size(rp,2)+length(h)-1;
%         rngpro=zeros(m,ns);
%         for k=1:m
%                 rngpro(k,:)=conv(h,rp(k,:,1));
%         end
        
       %% MTI v2
        %     [b,a]=butter(1, 0.01, 'high'); %  4th order is 24dB/octave slope, 6dB/octave per order of n
        % %                                      [B,A] = butter(N,Wn, 'high') where N filter order, b (numerator), a (denominator), ...
        % %                                      highpass, Wn is cutoff freq (half the sample rate)
        %     [m,n]=size(rp(:,:,1));
        %     rngpro=zeros(m,n);
        %     for k=1:size(rp,1)
        %         rngpro(k,:)=filter(b,a,rp(k,:,1));
        %     end
      %% STFT
%             rBin = min(cfar_bins(1)):1+max(cfar_bins(2)); %covid 18:30, front ignore= 7:nts/2, %lab 15:31 for front
        %     for i = 1:size(cfar_bins,2) % fill zeros
        %             if cfar_bins(1,i) == 0 || cfar_bins(2,i) == 0
        %                     cfar_bins(:,i) = cfar_bins(:,i-1);
        %             end
        %     end
        
%         rBin = min(cfar_bins(cfar_bins>0)):median(cfar_bins(2,:));
        rBin = 10:25;
        nfft = 2^12;window = 256;noverlap = 200;shift = window - noverlap;
        sx = myspecgramnew(sum(rp(rBin,:,12)),window,nfft,shift); % mti filter and IQ correction
        
      %% cfar bins
        %
        %     numrep = floor(ns/size(cfar_bins,2));
        %     b = ones(1,numrep);
        %     extended_bins = kron(cfar_bins,b);
        %     extended_bins(:,end+1:ns) = repmat(extended_bins(:,end),1,ns-size(extended_bins,2))+1;
        %     mask = zeros(size(rngpro));
        %     for i = 1:ns
        %             mask(extended_bins(1,i):extended_bins(2,i),i) = 1;
        %     end
        %     rngpro2 = rngpro.*mask;
        %     num_used = sum(mask);
        %     sx = myspecgramnew(sum(rngpro2)./num_used,window,nfft,shift); % mti filter and IQ correction
        
        sx2 = abs(flipud(fftshift(sx,1)));
        %% Spectrogram
        timeAxis = (1:NPpF*NoF)*SweepTime/NPpF*numTX ; % Time
        freqAxis = linspace(-prf/2,prf/2,nfft); % Frequency Axis
        
%         start_time = 1.5;
%         sx2 = sx2(:, size(sx2,2)/timeAxis(end)*start_time: end);
        
        figure('visible','on');
        colormap(jet(256));
        imagesc(timeAxis,[-prf/2 prf/2],20*log10(sx2./max(sx2(:))));
        set(gcf,'units','normalized','outerposition',[0,0,1,1]);
        %     axis xy
        %     set(gca,'FontSize',10)
        %     title(['RBin: ',num2str(rBin)]);
%         title(fOut(end-28:end-10))
%             xlabel('Time (sec)');
%             ylabel('Frequency (Hz)');
        caxis([-45 0]) % 40
        title('Micro-Doppler Spectrogram');
        set(gca, 'YDir','normal')
        %     colorbar;
        axis([0 timeAxis(end) -prf/2 prf/2])
        %     saveas(fig,[fOut(1:end-4) '.fig']);
        set(gca,'xtick',[],'ytick',[])
        frame = frame2im(getframe(gca));
        imwrite(frame,[fOut(1:end-4) '.png']);
        close all
        
end