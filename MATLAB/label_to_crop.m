clc; clear; close all;

sub = '14 jan ashwanth zeki';
main = '/mnt/HDD01/rspl-admin/DATASETS/Fall Sequential/Outputs/';
labels = [main sub '/labels/microDoppler/*.txt'];
crops = [main sub '/microDoppler/cut/'];

if ~exist(crops,'dir')
                mkdir(crops);
end
labels = dir(labels);

for i = 1:length(labels)
        msg = strcat(['Processing file ', int2str(i), ' of ', int2str(length(labels))]);   % loading message
        disp(msg);
        fname = labels(i).name(1:end-4);
        y = textread([labels(i).folder '/' labels(i).name]);
        img = imread([crops(1:end-4) fname '.png']);
        for j = 1:18
             idx = find(y==j); 
             if idx
                     crop = img(:,min(idx):max(idx),:);
                     cropname = [crops fname '_' num2str(j) '.png'];
                     imwrite(crop,cropname)
             end
        end
        
end