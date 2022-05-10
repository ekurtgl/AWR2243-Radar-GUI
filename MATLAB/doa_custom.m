clc; clear; close all; warning off;

files = dir('..\DOA test\*.bin');
idcs = [13:22 25:27];

for  k = 13:length(idcs) % 8, 9, 12, 13
idx = idcs(k);
fname = fullfile(files(idx).folder, files(idx).name);
RDC = RDC_extract(fname);
K = [1];
M_range = [1];
M_pulse = 256;
MTI = false;
OF = false;
for i = 1:length(K)
    for j = 1:length(M_range)
        mss = ['Processing File: ' int2str(k) '/' int2str(length(idcs)) ', ' int2str((i-1)*length(M_range)+j) '/' int2str(length(K)*length(M_range))];
        disp(mss);
        fout = [fname(1:end-4) '_K' int2str(K(i)) '_Mrange' int2str(M_range(j)) '_Mpulse' int2str(M_pulse) '_MTI' int2str(MTI) '_OF' int2str(OF) '.avi'];
        RDC_to_rangeDOA_AWR1642(RDC, K(i), M_range(j), M_pulse, MTI, OF, fout)
        RDC_to_rangeDOA_AWR1642_microDoppler(RDC, K(i), M_range(j), M_pulse, MTI, OF, fout)
    end
end
end
