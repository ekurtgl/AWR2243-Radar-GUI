clc; clear; close all

data = '/media/rspl-admin/Seagate Backup Plus Drive/Sequential Fall/';
main = [data 'Outputs/'];

subs = dir(main);
subs = subs(3:end);
seqPerRecord = 5; 

for s = 5:length(subs)
        rdc_fold =  [subs(s).folder '/' subs(s).name '/RDC/'];

        if ~exist(rdc_fold,'dir')
                mkdir(rdc_fold);
        end

        label_path = [subs(s).folder '/' subs(s).name '/labels/microDoppler/*.txt' ];
        labels = dir(label_path);
        
        l_uniq = {labels.name};
        func = @(c) c(1:end-6);
        l_uniq2 = cellfun(func, l_uniq, 'UniformOutput',false);
        l_uniq3 = unique(l_uniq2);
        
        files = dir([data subs(s).name '/77ghz/Front/*.bin']);
        filenames2 = {files.name};
        if s ==5
                z=38;
        else
                z=1;
        end
        for j = z:length(l_uniq3)
                
                match = strfind(filenames2,l_uniq3{j}); % find matches
                idx = find(~cellfun(@isempty,match)); % find non-empty indices
                RDC = [];
                for r = 1:length(idx)
                        fname = fullfile(files(idx(r)).folder,files(idx(r)).name);
                        temp2 = RDC_extract(fname);
                        RDC = [RDC temp2];
                end
                numChirps = floor(size(RDC,2)/seqPerRecord);
                
                match2 = strfind(l_uniq,l_uniq3{j}); % find matches
                idx2 = find(~cellfun(@isempty,match2)); % find non-empty indices
                
                for r =1:length(idx2)
                         
                         msg = ['Processing: Subject ' subs(s).name ', File: ' int2str(j) ' of ' int2str(length(l_uniq)) ', Part ' ...
                                 num2str(r) '/' num2str(length(idx2))];   % loading message
                         disp(msg);
                         subRDC = RDC(:,(r-1)*numChirps+1:r*numChirps,:);
                         y_file = [labels(idx2(r)).folder '/' labels(idx2(r)).name]; 
                         y_md = textread(y_file);
                         ratio = numChirps/length(y_md);
                         y_rdc = repelem(y_md,floor(ratio));
                         y_rdc = [y_rdc zeros(1,numChirps-length(y_rdc))];
                         
                         state = y_rdc(1);
                         start = 1;
                         for i = 1:length(y_rdc)
                                 if y_rdc(i) == state
                                         continue
                                 else
                                       stop = i-1;  
                                       crop = subRDC(:,start:stop,:);
                                       rdcname = [rdc_fold labels(idx2(r)).name(1:end-4) '_' num2str(state) '.mat'];
                                       save(rdcname, 'crop');
                                       start = i;
                                       state = y_rdc(i);
                                 end
                                 
                         end
                 end
        end
end















