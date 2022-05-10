function [cfar_bins] = RDC_to_rangeDopp( RDC, fNameOut, fnameBin )
        
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
        
        %% Range-Velocity Map
        
        Rmax = sampleFreq*c/(2*slope);
        Tc = idletime+adcStartTime+rampEndTime;
        Tf = SweepTime;
        velmax = lambda/(Tc*4); % Unambiguous max velocity
        DFmax = velmax/(c/fc/2);
        rResol = c/(2*Bw);
        vResol = lambda/(2*Tf);
        % define frame size
        PN = NTS; %10 equally time spaced matricex: 10X500=5000
        RANGE_FFT_SIZE = NTS;
        DOPPLER_FFT_SIZE = PN*2; %*2
        
        
        RNGD2_GRID = linspace(0, Rmax, RANGE_FFT_SIZE);
        DOPP_GRID = linspace(DFmax, -DFmax, DOPPLER_FFT_SIZE);
        
        V_GRID = (c/fc/2)*DOPP_GRID;
        
        RCData = RDC(:,:,1);
        fps = 25;%1/SweepTime;
        n_frames = duration*fps;
        shft = floor(size(RCData,2)/n_frames);
        
      %%  CA-CFAR params
        numGuard = 4;
        numTrain = numGuard*2;
        P_fa = 1e-5; % Prob of false alarm
        SNR_OFFSET = -5; % -10
        %     cfar_bins = ones(2,n_frames);
        figure('Visible','off')%,
        % set(gcf,  'units', 'normalized','position', [0.2 0.2 0.4 0.6])
        
        for k = 1:n_frames
                
                RData_frame = RCData(:, 1+(k-1)*shft:k*shft);
                RData_frame = bsxfun(@minus, RData_frame, mean(RData_frame,2));   % subtract stationary objects
                G_frame = fftshift(fft2(RData_frame, RANGE_FFT_SIZE,DOPPLER_FFT_SIZE),2); % 2 adjust  shift
                RDM_dB = 10*log10(abs(G_frame)./max(abs(G_frame(:))));
                %         time_Counter = (k/n_frames)*duration;
                [~, cfar_ranges, ~] = ca_cfar(RDM_dB, numGuard, numTrain, P_fa, SNR_OFFSET);
                if ~isempty(cfar_ranges)
                        cfar_bins(1,k) = min(cfar_ranges);
                        cfar_bins(2,k) = max(cfar_ranges);
                else
                        cfar_bins(1,k) = 17;
                        cfar_bins(2,k) = 35;
                end
                
                imagesc(V_GRID,RNGD2_GRID,RDM_dB);
                %         xlabel('Radial Velocity (m/s)','FontSize',13, 'FontName','Times')
                %         ylabel('Range (meter)','FontSize',13, 'FontName','Times')
                %         title({'Range-Velocity Map';num2str(time_Counter,'%.2f')},'FontSize',13, 'FontName','Times')
                %         colorbar
                set(gca, 'CLim',[-10,0]); % [-35,0],
                colormap(jet) % jet
                %         caxis([90 130]) % 90 130
                %         axis xy;
                axis([-velmax/numTX velmax/numTX 0 4])
                %         set(gcf, 'Position',  [100, 100, size(G_frame,1), size(G_frame,2)])
                
                drawnow
                F(k) = getframe(gca); % gcf returns the current figure handle
                
                %       colormap(gray)
                %       F2(k) =  getframe(gca);
                
        end
        
        %     fGray = [fNameOut(1:end-4) '_gray.avi'];
        
        writerObj = VideoWriter(fNameOut);
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