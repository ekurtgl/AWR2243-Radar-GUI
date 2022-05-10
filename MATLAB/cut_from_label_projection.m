clc; clear; close all

impath = '/mnt/HDD02/Projection/Spectrograms/';
rdcpath = '/mnt/HDD02/Projection/RDCs/';
labelpath = '/mnt/HDD02/Projection/Spectrograms/labels/md/*.txt';
imout = [impath 'cut/'];
rdcout = [rdcpath 'cut/'];
files = dir(labelpath);

for j =1:length(files)
         
         im = imread([impath files(j).name(1:end-4) '.png']);
         rdc = load([rdcpath files(j).name(1:end-4) '.mat']);
         rdc = rdc.RDC;
         
         y_md = textread([files(j).folder '/' files(j).name]);
         ratio = length(rdc)/length(im);

         state = y_md(1);
         start = 1;
         cnt = 1;
         
         for i = 1:length(y_md)
                 if y_md(i) == state
                         if state == 0
                                 start = i;
                         end
                         continue
                 else
                         stop = i-1;
                         if state ~= 0
                                 msg = ['Processing ' int2str(j) '/' int2str(length(files)) ', crop #' int2str(cnt)];   % loading message
                                 disp(msg);
                                 crop = imresize(im(:,start:stop,:),[256 256]);
%                                  crop = im(:,start:stop,:);
                                 cropname = [imout files(j).name(1:end-4) '_' int2str(cnt) '.png'];
                                 imwrite(crop, cropname);
                                 crop_rdc = rdc(:,round(start*ratio):round(stop*ratio),:);
                                 save([rdcout files(j).name(1:end-4) '_' int2str(cnt) '.mat'], 'crop_rdc');
                                 cnt = cnt + 1;
                         end
                         start = i;
                         state = y_md(i);
                 end

         end
end
