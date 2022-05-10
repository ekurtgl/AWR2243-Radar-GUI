function [] = microDoppler_AWR1642_bulk_BPM(fname, fOut)
    % read .bin file
    fid = fopen(fname,'r');
    % DCA1000 should read in two's complement data
    Data = fread(fid, 'int16');
    fclose(fid);
    %% Parameters
    fileSize = size(Data, 1);

    numADCBits = 16; % number of ADC bits per sample
    SweepTime = 40e-3; % Time for 1 frame
    NTS = 256; %256 Number of time samples per sweep
    numADCSamples = NTS;
    numTX = 1; % '1' for 1 TX, '2' for BPM
    NoC = 128;%128; % Number of chirp loops
    NPpF = numTX*NoC; % Number of pulses per frame
    numRX = 4;
    
    numLanes = 2; % do not change. number of lanes is always 4 even if only 1 lane is used. unused lanes
    % NoF = fileSize/2/NPpF/numRX/NTS; % Number of frames
    numChirps = ceil(fileSize/2/NTS/numRX);
    NoF = round(numChirps/NPpF); % Number of frames, 4 channels, I&Q channels (2)
    Np = numChirps;%floor(size(Data(:,1),1)/NTS); % #of pulses
    dT = SweepTime/NPpF; % 
    prf = 1/dT; %
    isReal = 0; % set to 1 if real only data, 0 if complex dataare populated with 0 %% read file and convert to signed number

    %% Data reshape
    % if 12 or 14 bits ADC per sample compensate for sign extension
    if numADCBits ~= 16
        l_max = 2^(numADCBits-1)-1;
        Data(Data > l_max) = Data(Data > l_max) - 2^numADCBits;
    end

    % real data reshape, filesize = numADCSamples*numChirps
    if isReal
        numChirps = fileSize/numADCSamples/numRX;
        LVDS = zeros(1, fileSize);
        %create column for each chirp
        LVDS = reshape(Data, numADCSamples*numRX, numChirps);
        %each row is data from one chirp
        LVDS = LVDS.';
    else
        % for complex data
    %     numChirps = fileSize/2/numADCSamples/numRX;
        LVDS = zeros(1, fileSize/2);
        %combine real and imaginary part into complex data
        %read in file: 2I is followed by Q
    end

    %% Data format in swra581b.pdf
    LVDS(1:2:end) = Data(1:4:end) + sqrt(-1)*Data(3:4:end);
    LVDS(2:2:end) = Data(2:4:end) + sqrt(-1)*Data(4:4:end);
    
    % check array size (if any frames were dropped, pad zeros)
    if length(LVDS) ~= numADCSamples*numRX*numChirps
       numpad =  numADCSamples*numRX*numChirps - length(LVDS); % num of zeros to be padded
       LVDS = padarray(LVDS, [0 numpad],'post');
    end
    % create column for each chirp
    LVDS = reshape(LVDS, numADCSamples*numRX, double(numChirps));
    %% If BPM, i.e. numTX = 2, see MIMO Radar sec. 4.2
    BPMidx = [1:2:numChirps-1];
    if numTX == 2
       LVDS_TX0 = 1/2 * (LVDS(:,BPMidx)+LVDS(:,BPMidx+1));
       LVDS_TX1 = 1/2 * (LVDS(:,BPMidx)-LVDS(:,BPMidx+1));
       LVDS0 = kron(LVDS_TX0,ones(1,2));
       LVDS1 = kron(LVDS_TX1,ones(1,2));
       LVDS = zeros(NTS*numRX*numTX,numChirps);
       LVDS(1:end/2,:) = LVDS0;
       LVDS(end/2+1:end,:) = LVDS1;
    end
    clear LVDS0 LVDS1 LVDSTX0 LVDSTX1 Data
    %% Organize data per RX
    Data = zeros(numChirps*numADCSamples, numRX*numTX);
    for i = 1:numRX*numTX
        Data(:,i) = reshape(LVDS((i-1)*numADCSamples+1:i*numADCSamples,:),[],1);
    end

    %% No IQ Correction
    rawData = reshape(Data,NTS,numChirps, numRX*numTX); 
    rp = fft(rawData);
    clear Data
     %% MTI Filter (not working)
    [m,n]=size(rp(:,:,1));
%     ns = size(rp,2)+4;
    h=[1 -2 3 -2 1]';
    ns = size(rp,2)+length(h)-1;
    rngpro=zeros(m,ns);
    for k=1:m
        rngpro(k,:)=conv(h,rp(k,:,1));
    end
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
    rBin = 15:35; %covid 18:30, front ignore= 7:nts/2, %lab 15:31 for front
    nfft = 2^12;window = 256;noverlap = 240;shift = window - noverlap;
%      sx = myspecgramnew(rngpro(rBin,:),window,nfft,shift);
     sx = myspecgramnew(sum(rngpro(rBin,:)),window,nfft,shift); % mti filter and IQ correction
    sx2 = abs(flipud(fftshift(sx,1)));
    %% Spectrogram
    timeAxis = [1:NPpF*NoF]*SweepTime/NPpF ; % Time
    freqAxis = linspace(-prf/2,prf/2,nfft); % Frequency Axis
    fig = figure('visible','off');
    colormap(jet(256));
    doppSignMTI = imagesc(timeAxis,[-prf/2 prf/2],20*log10(abs(sx2/max(sx2(:)))));
    set(gcf,'units','normalized','outerposition',[0,0,1,1]);
%     axis xy
%     set(gca,'FontSize',10)
%     title(['RBin: ',num2str(rBin)]);
    title(fOut(end-28:end-10))
%     xlabel('Time (sec)');
%     ylabel('Frequency (Hz)');
    caxis([-45 0]) % 40
    set(gca, 'YDir','normal')
%     colorbar;
    axis([0 timeAxis(end) -prf/6 prf/6])
    saveas(fig,[fOut(1:end-4) '.fig']);
    set(gca,'xtick',[],'ytick',[])
    frame = frame2im(getframe(gca));
    imwrite(frame,[fOut(1:end-4) '.png']);
    close all
end