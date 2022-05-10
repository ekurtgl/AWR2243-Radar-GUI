function [] = RDC_to_rangeDOA_AWR1642_microDoppler(RDC, MTI, fNameOut)
        
        numTX = 2;
        numRX = 4;
        NTS = size(RDC,1); %64 Number of time samples per sweep
        NoC = 128; % Number of chirp loops
        NPpF = numTX*NoC; % Number of pulses per frame
        fstart = 77e9; % Start Frequency
        fstop = fstart+4e9;%1.79892e9;%   Stop Frequency
        sampleFreq = 6.25e6; % 2e6 ADC Sampling frequency
        slope = 66.578e12; %29.982e12; % Mhz / us = e6/e-6 = e12
        %     numADCBits = 16; % number of ADC bits per sample
        
        fc = (fstart+fstop)/2; % Center Frequency
        c = physconst('LightSpeed'); % Speed of light
        lambda = c/fc; % Lambda
        d = lambda/2; % element spacing (in wavelengths)
        SweepTime = 40e-3; % Time for 1 frame=sweep
        numChirps = size(RDC,2);
        NoF = round(numChirps/NPpF); % Number of frames, 4 channels, I&Q channels (2)
        Bw = fstop - fstart; % Bandwidth
        
        dT = SweepTime/NPpF; %
        prf = 1/dT;
        timeAxis = linspace(0,SweepTime*NoF,numChirps);%[1:NPpF*NoF]*SweepTime/NPpF ; % Time
        duration = max(timeAxis);
        
        idletime = 100e-6;
        adcStartTime = 6e-6;
        rampEndTime = 60e-6;
        
        %% Range Angle Map
        
        Rmax = sampleFreq*c/(2*slope);
        rResol = c/(2*Bw);
        
        RANGE_FFT_SIZE = NTS;
        RNGD2_GRID = linspace(0, Rmax, RANGE_FFT_SIZE);
        
        fps = 25;%1/SweepTime;
        n_frames = duration*fps;
        shft = floor(size(RDC,2)/n_frames);
        
        figure('visible','off')
        colormap(jet)
        
%         opticFlow = opticalFlowHS;
        
        %% MTI
        h = [1 -2 1]; % [1 -2 1]
        if MTI
            RDC2 = bsxfun(@minus, RDC, mean(RDC,2));   % subtract stationary objects
            MTI_out  = filter(h,1,RDC2,[],2);
            rangeFFT = fft(MTI_out, RANGE_FFT_SIZE);
        else 
            rangeFFT = fft(RDC, RANGE_FFT_SIZE);
        end
        
        %% original spect
        rBin = 15:35;
        nfft = 2048;window = 256;noverlap = 200;shift = window - noverlap;
        sx = myspecgramnew(sum(rangeFFT(rBin,:,1)),window,nfft,shift); 
        sx2 = abs(flipud(fftshift(sx,1)));
        figure('visible','off');
        colormap(jet(256));
        imagesc(timeAxis,[-prf/2 prf/2],20*log10(sx2));
        colorbar;
%         set(gcf,'units','normalized','outerposition',[0,0,1,1]);
%          caxis([-45 0]) % 40
        clim = get(gca,'CLim');
        set(gca, 'YDir','normal','clim',[clim(1)+90 clim(2)])
        axis([0 timeAxis(end) -prf/6 prf/6])
        
        ylabel('Frequency (Hz)');
        xlabel('Times (s)');
        frame = frame2im(getframe(gcf));
        imwrite(frame,[fNameOut(1:end-4) '_orig.png']);
        %% angle
        
        ang_ax = -90:90;
        d = 0.5;
        
        for k=1:length(ang_ax)
                a1(:,k)=exp(-1i*2*pi*(d*(0:numTX*numRX-1)'*sin(ang_ax(k).'*pi/180)));
        end
%         B_left = a1(:,round(end/6)+1:round(end/2)-1); % -60 to 0
%         B_right = a1(:,round(end/2)+1:round(5*end/6)); % 0 to 60
%         B_left = a1(:,round(end/6)+1:round(2*end/6)-1); % -60 to -30
%         B_right = a1(:,round(4*end/6)+1:round(5*end/6)); % 30 to 60
        for i = 1:1%9 % divide into 10 degrees, set limit to 9
            
%         B_left = a1(:,(i-1)*10+1:i*10); % 10 degree intervals
%         B_right = a1(:,(i+8)*10+1:(i+9)*10); % 10 degree intervals
%         B_left = a1(:,1:floor(end/2)); % -90 to 0
%         B_right = a1(:,ceil(end/2)+1:end); % 0 to 90
%         B_left = a1(:,round(end/6)+1:round(end/2)-1); % -60 to 0
%         B_right = a1(:,round(end/2)+1:round(5*end/6)); % 0 to 60
        B_left = a1(:,1:round(end/3)-1); % -60 to 0
        B_right = a1(:,round(2*end/3)+1:end); % 0 to 60
        
        B_herm_left = B_left*inv(B_left'*B_left)*B_left';
        B_herm_right = B_right*inv(B_right'*B_right)*B_right';
        
        RDC_left = zeros(size(rangeFFT));
        RDC_right = zeros(size(rangeFFT));
        for c = 1:size(rangeFFT,2)
            for r = 1:size(rangeFFT,1)
                x = squeeze(rangeFFT(r,c,:));
                y_left = B_herm_left*x;
                y_right = B_herm_right*x;
                RDC_left(r,c,:) = y_left;
                RDC_right(r,c,:) = y_right;
            end
        end
        
        
        %% right
        sx = myspecgramnew(sum(RDC_right(rBin,:,1)),window,nfft,shift); 
        sx2 = abs(flipud(fftshift(sx,1)));
        figure('visible','off');
        colormap(jet(256));
        imagesc(timeAxis,[-prf/2 prf/2],20*log10(sx2));
        colorbar;
%         set(gcf,'units','normalized','outerposition',[0,0,1,1]);
%          caxis([-45 0]) % 40
        clim = get(gca,'CLim');
        set(gca, 'YDir','normal','clim',[clim(1)+90 clim(2)])
        axis([0 timeAxis(end) -prf/6 prf/6])
        ylabel('Frequency (Hz)');
        xlabel('Times (s)');
        frame = frame2im(getframe(gcf));
%         imwrite(frame,[fNameOut(1:end-4) '_right_' int2str(i) '.png']);
        imwrite(frame,[fNameOut(1:end-4) '_right_30to90.png']);
        %% left
        sx = myspecgramnew(sum(RDC_left(rBin,:,1)),window,nfft,shift); 
        sx2 = abs(flipud(fftshift(sx,1)));
        figure('visible','off');
        colormap(jet(256));
        imagesc(timeAxis,[-prf/2 prf/2],20*log10(sx2));
%         set(gcf,'units','normalized','outerposition',[0,0,1,1]);
%          caxis([-45 0]) % 40
        clim = get(gca,'CLim');
        colorbar;
        set(gca, 'YDir','normal','clim',[clim(1)+90 clim(2)])
        axis([0 timeAxis(end) -prf/6 prf/6])
        ylabel('Frequency (Hz)');
        xlabel('Times (s)');
        frame = frame2im(getframe(gcf));
%         imwrite(frame,[fNameOut(1:end-4) '_left_' int2str(i) '.png']);
        imwrite(frame,[fNameOut(1:end-4) '_left_-90to-30.png']);
        end
end