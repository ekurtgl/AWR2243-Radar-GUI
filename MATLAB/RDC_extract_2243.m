function RDC = RDC_extract_2243(fNameIn)
    fileID = fopen(fNameIn, 'r'); % open file
    RDC = fread(fileID, 'int16');% DCA1000 should read in two's complement data
    fclose(fileID); % close file
    
    fileSize = size(RDC, 1);
    isBPM = 1;
    isTDM = 1;
    numRX = 4;
    NTS = 256; % Number of time samples per sweep
    numChirps = ceil(fileSize/2/NTS/numRX);
    
    %% Organize data per RX
    
    zerostopad = NTS*numChirps*numRX*2-length(RDC);
    RDC = [RDC; zeros(zerostopad,1)];
    
    RDC = reshape(RDC, 2*numRX, []);
    RDC = RDC(1:4,:) + sqrt(-1)*RDC(5:8,:);                                  
    RDC = RDC.';
    
    RDC = reshape(RDC,NTS,numChirps,numRX); 
    
    
    %% If BPM, i.e. numTX = 2, see MIMO Radar sec. 4.2
    
    if isBPM && isTDM
            rem = mod(size(RDC,2), 3);
            rem
            if rem ~= 0
                RDC(:,end-(3-rem)-1:end,:) = [];
            end
            size(RDC)
            % decompose the chirps
            chirp1 = 1/2 * (RDC(:, 1:3:end, :) + RDC(:, 2:3:end, :));
            chirp2 = 1/2 * (RDC(:, 1:3:end, :) - RDC(:, 2:3:end, :));
            chirp3 = RDC(:, 3:3:end, :); % elevation
            RDC = cat(3, chirp1, chirp2, chirp3);
    end
    
end