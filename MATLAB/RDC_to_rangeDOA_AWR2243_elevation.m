function [] = RDC_to_rangeDOA_AWR2243_elevation(RDC, K, M_pulse, MTI, OF, fNameOut)
        
        numTX = 3;
        numRX = 2;
        NTS = size(RDC,1); %64 Number of time samples per sweep
        NoC = 88; % Number of chirp loops
        NPpF = numTX*NoC; % Number of pulses per frame
        fstart = 77e9; % Start Frequency
        fstop = fstart+4e9;%1.79892e9;%   Stop Frequency
        sampleFreq = 5.688e6; % 2e6 ADC Sampling frequency
        slope = 80e12; %29.982e12; % Mhz / us = e6/e-6 = e12
        %     numADCBits = 16; % number of ADC bits per sample
        
        fc = (fstart+fstop)/2; % Center Frequency
        c = physconst('LightSpeed'); % Speed of light
        lambda = c/fc; % Lambda
        d = lambda/2; % element spacing (in wavelengths)
        SweepTime = 40e-3; % Time for 1 frame=sweep
        numChirps = size(RDC,2);
        NoF = round(numChirps/NPpF*numTX); % Number of frames, 4 channels, I&Q channels (2)
        Bw = fstop - fstart; % Bandwidth
        
        dT = SweepTime/NPpF; %
        prf = 1/dT;
        timeAxis = linspace(0,SweepTime*NoF,numChirps);%[1:NPpF*NoF]*SweepTime/NPpF ; % Time
        duration = max(timeAxis);
        
        idletime = 100e-6;
        adcStartTime = 5e-6;
        rampEndTime = 50e-6;
        
        %% If BPM and TDM, merge 3rd channel of antenna 1 and 1st channel of antenna 2
%         RDC = cat(3, RDC(:, :, 3), RDC(:, :, 9));
        RDC = cat(3, sum(RDC(:, :, 3:6), 3), sum(RDC(:, :, 9:end), 3));
        
        %% Range Angle Map
        
        Rmax = sampleFreq*c/(2*slope);
        rResol = c/(2*Bw);
        
        RANGE_FFT_SIZE = NTS;
        RNGD2_GRID = linspace(0, Rmax, RANGE_FFT_SIZE);
        
        fps = 25; % 1/SweepTime;
        n_frames = duration*fps;
        shft = floor(size(RDC,2)/n_frames);
        
        figure('visible','off')
        colormap(jet)
        
        opticFlow = opticalFlowHS;
        numTX2 = 1; % if BPM and TDM keep this 1 for elevation
        
        %% MTI
        h = [1 -2 1]; % [1 -2 1]
        if MTI
            RDC2 = bsxfun(@minus, RDC, mean(RDC,2));   % subtract stationary objects
            MTI_out  = filter(h,1,RDC2,[],2);
            rangeFFT = fft(MTI_out, RANGE_FFT_SIZE);
        else 
            rangeFFT = fft(RDC, RANGE_FFT_SIZE);
        end
        RNGD2_GRID = linspace(0, Rmax, size(rangeFFT,1));
        ratio = size(rangeFFT,1)/Rmax;
        rangelim = max(RNGD2_GRID);% meters
        rangelimMatrix = ceil(ratio*rangelim);
        ang_ax = -90:90;
        d = 0.5;
        
        for k=1:length(ang_ax)
                a1(:,k)=exp(-1i*2*pi*(d*(0:numTX2*numRX-1)'*sin(ang_ax(k).'*pi/180)));
        end
        
        for j = 1:n_frames
                disp([int2str(j) '/' int2str(n_frames)]);
                for i = 1:size(rangeFFT,1)
%                         Rxx = zeros(numTX*numRX,numTX*numRX);
%                         for m = 1:M
%                                 if j >= n_frames - M
%                                         idx = (j-1)*NoC*numTX-(m-1)*NoC*numTX+1;
%                                         A = squeeze(rangeFFT(i,idx,:));
% %                                         idx = (j-1)*NoC*numTX-m+1:j*NoC*numTX;
% %                                         A = squeeze(sum(rangeFFT(i,idx,:),2));
%                                 else
%                                         idx = (j-1)*NoC*numTX+(m-1)*NoC*numTX+1;
%                                         A = squeeze(rangeFFT(i,idx,:));
% %                                         idx = (j-1)*NoC*numTX+1:j*NoC*numTX+m;
% %                                         A = squeeze(sum(rangeFFT(i,idx,:),2));
%                                 end
% %                                 A = squeeze(sum(rangeFFT(i,(j-1)*(m-1)*NoC*numTX+1:(j-1)*m*NoC*numTX,:),2));
%                                 Rxx = Rxx + 1/M * (A*A');
%                         end
%                         idx = (j-1)*NoC*numTX+1:(j-1)*NoC*numTX+M;
%                         A = squeeze(sum(rangeFFT(i,idx,:),2));
                        
%                         Rxx = 1/M * (A*A'); 
                        Rxx = zeros(numTX2*numRX,numTX2*numRX);
                            
                        for mp = 1:M_pulse
                            p_idx = (j-1)*(NPpF/numTX)+mp;
                            if j == n_frames
                                p_idx = (j-2)*(NPpF/numTX)+mp;
                            end
                            A = squeeze(rangeFFT(i,p_idx,:));
                            Rxx = Rxx + 1/(M_pulse) * (A*A');
                        end
                        
                        [Q,D] = eig(Rxx); % Q: eigenvectors (columns), D: eigenvalues
                        [D, I] = sort(diag(D),'descend');
                        Q = Q(:,I); % Sort the eigenvectors to put signal eigenvectors first
                        Qs = Q(:,1:K); % Get the signal eigenvectors
                        Qn = Q(:,K+1:end); % Get the noise eigenvectors
                        
                        for k=1:length(ang_ax)
                                music_spectrum2(k)=(a1(:,k)'*a1(:,k))/(a1(:,k)'*(Qn*Qn')*a1(:,k));
                        end
                        
                        range_az_music(i,:) = music_spectrum2;
                end
                
                if OF
                    f2 = abs(range_az_music); %imresize(frame2im(F2), 0.5);
                    flow = estimateFlow(opticFlow,f2);
                    magnitudes = flow.Magnitude;
                    imagesc(ang_ax,RNGD2_GRID(1:rangelimMatrix),20*log10(abs(range_az_music(1:rangelimMatrix,:)) .* magnitudes(1:rangelimMatrix,:) ./ max(max(abs(range_az_music((1:rangelimMatrix),:))))));
                    set(gca, 'CLim',[-25,0]);
                else
                    imagesc(ang_ax,RNGD2_GRID(1:rangelimMatrix),20*log10(abs(range_az_music(1:rangelimMatrix,:))./max(abs(range_az_music(:)))));
                    
                end
                
                xlabel('Elevation')   
                ylabel('Range (m)')
%                 set(gca, 'CLim',[-35,0]); % [-35,0]
                axis([-60 60 0 3])
%                 title('MUSIC Range-Angle Map')
%                 clim = get(gca,'clim');
                drawnow
                F(j) = getframe(gcf); % gcf returns the current figure handle
                
        end
        
        
        fname = [fNameOut(1:end-4) '_K' int2str(K) '_Mpulse' ...
            int2str(M_pulse) '_MTI' int2str(MTI) '_OF' int2str(OF) '_elevation.avi'];
        writerObj = VideoWriter(fname);
        writerObj.FrameRate = fps;
        open(writerObj);
        
        %     writerObj2 = VideoWriter(fGray);
        %     writerObj2.FrameRate = fps;
        %     open(writerObj2);
        
        for i=1:length(F)
                % convert the image to a frame
                frame = F(i) ;
                writeVideo(writerObj, frame);
                %         frame2 = F2(i);
                %         writeVideo(writerObj2, frame2);
        end
        close(writerObj);
        %     close(writerObj2);
        close all
end