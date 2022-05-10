function [] = microDoppler_AWR2243_bulk_BPM(fname, fOut)
    % read .bin file
    
    fid = fopen(fname,'r');
    
    % DCA1000 should read in two's complement datata
    Data = fread(fid, 'int16');
    fclose(fid);
    %% Parameters
    fileSize = size(Data, 1);

    numADCBits = 16; % number of ADC bits per sample
    SweepTime = 40e-3; % Time for 1 frame
    NTS = 256; %256 Number of time samples per sweep
    numADCSamples = NTS;
    numTX = 1; % '1' for 1 TX, '3' for BPM
    NoC = 252 ;%128; % Number of chirp loops
    NPpF = numTX*NoC; % Number of pulses per frame
    numRX = 4;
    isBPM = 1; % is bpm enabled? 1 or 0
    
    numLanes = 2; % do not change. number of lanes is always 4 even if only 1 lane is used. unused lanes
    numChirps = ceil(fileSize/2/NTS/numRX);
    NoF = round(numChirps/NPpF); % Number of frames, 4 channels, I&Q channels (2)
    duration = SweepTime*NoF;
    dT = SweepTime/NPpF; % 
    prf = 1/dT; %
    
    %% Data pad zeros
    if length(Data) ~= numADCSamples*numChirps*numRX*2
       numpad =  numADCSamples*numRX*numChirps - length(Data); % num of zeros to be padded
       Data = padarray(Data, [0 numpad],'post');
    end
    
    %% Reshape the data acc to the raw data format
    Data = reshape(Data, numLanes*4, []);
    Data = Data(1:4,:) + sqrt(-1)*Data(5:8,:);                                  
    Data = Data.';
   
    %% If BPM, i.e. numTX = 3, see MIMO Radar sec. 4.2
%     S1  + S2 + S3 = m1 ; 
%     S1  + S2 - S3 = m2 ;
%     S1  - S2 + S3 = m3 ;
%     -------------------
%     S1 = (m2 + m3)/2;
%     S2 = (m1 – m3)/2;
%     S3 = (m1 – m2)/2;
    m1 = 1:3:length(Data);
    if isBPM 
       LVDS_TX1 = (Data(m1+1,:) + Data(m1+2,:))/2;
       LVDS_TX2 = (Data(m1,:) - Data(m1+2,:))/2;
       LVDS_TX3 = (Data(m1,:) + Data(m1+1,:))/2;
       Data = cat(2,LVDS_TX1,LVDS_TX2,LVDS_TX3);
    end
    Data = reshape(Data,NTS,[],numRX*numTX);
    rp = fft(Data); % range FFT
    clear Data
     %% MTI Filter (not working)
%     [m,n]=size(rp(:,:,1));
% %     ns = size(rp,2)+4;
%     h=[1 -2 3 -2 1]';
%     ns = size(rp,2)+length(h)-1;
%     rngpro=zeros(m,ns);
%     for k=1:m
%         rngpro(k,:)=conv(h,rp(k,:,1));
%     end
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
    rangepro = rp(:,:,1);
    rBin =  10:22; %covid 18:30, front ingore= 7:nts/2, %lab 15:31 for front
    nfft = 2^12;window = 256;noverlap = 200;shift = window - noverlap;
    sx = myspecgramnew(sum(rangepro(rBin,:)),window,nfft,shift); % mti filter and IQ correction
    sx2 = abs(flipud(fftshift(sx,1)));
    %% Spectrogram
    timeAxis = [1:NPpF*NoF]*SweepTime/NPpF ; % Time
    freqAxis = linspace(-prf/2,prf/2,nfft); % Frequency Axis
    fig = figure('visible','on');
    colormap(jet(256));
    set(gca,'units','normalized','outerposition',[0,0,1,1]);
    imagesc(timeAxis,[-prf/2 prf/2],20*log10(abs(sx2/max(sx2(:)))));
%     axis xy
%     set(gca,'FontSize',10)
    title(['RBin: ',num2str(rBin)]);
%     title(fOut(end-22:end-4))
%     xlabel('Time (sec)');
%     ylabel('Frequency (Hz)');
    caxis([-45 0]) % 40
    set(gca, 'YDir','normal')
    set(gcf,'color','w');
%     colorbar;
%    axis([0 timeAxis(end) -prf/6 prf/6])
%     saveas(fig,[fOut(1:end-4) '.fig']);
    set(gca,'xtick',[],'ytick',[])
    frame = frame2im(getframe(gca));
    imwrite(frame,[fOut(1:end-4) '.png']);
%     close all
end