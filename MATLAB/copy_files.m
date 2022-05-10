clc; clear; close all;

ims = 'C:\Users\emrek\Desktop\Villanova\spects\';
labels = dir('C:\Users\emrek\Desktop\Villanova\new labels\*.txt');
dest = 'C:\Users\emrek\Desktop\Villanova\augmented spec\';
for i = 1:length(labels)
   
    fname = labels(i).name;
    imname = [fname(1:end-4) '.png'];
    imfile = [ims imname];
    copyfile(imfile,[dest imname], 'f');
    
end





