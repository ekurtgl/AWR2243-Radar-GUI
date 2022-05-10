clc; clear; close all;

mainpath = 'D:\110signOutput\';
subjects = dir(mainpath);
subjects = subjects(3:12);
idx = 1:length(subjects);
ntv_idx = [3 4 5 7];
natives = subjects(ntv_idx);
imit_idx = idx;
imit_idx(ntv_idx) = [];
imits = subjects(imit_idx);

num_class = 110;

for i = 1:length(natives)
   ntvpath = [mainpath natives(i).name '\microDoppler\Cut\*.png'];
   ntvfiles{i} = dir(ntvpath);
end
ntv_f = cat(1,ntvfiles{:});
for i = 1:length(imits)
   imitpath = [mainpath imits(i).name '\microDoppler\Cut\*.png'];
   imitfiles{i} = dir(imitpath);
end
imit_f = cat(1,imitfiles{:});

for i = 1:num_class
    msg = ['Processing Class: ' num2str(i) '/' num2str(num_class)];
    disp(msg)
    str = ['_' num2str(i) '.png'];
    
    ntv_i = strfind({ntv_f.name},str);
    ntvid = find(~cellfun(@isempty,ntv_i));
    for j = 1:length(ntvid)
        ntv_im{j} = imresize(imread(fullfile(ntv_f(j).folder,ntv_f(j).name)),[128, 128]);
        [up,~,down] = env_find(ntv_im{j});
        ntv_env{j} = [up down];
    end
    
    imit_i = strfind({imit_f.name},str);
    imitid = find(~cellfun(@isempty,imit_i));
    for j = 1:length(imitid)
        imit_im{j} = imresize(imread(fullfile(imit_f(j).folder,imit_f(j).name)),[128, 128]);
        [up,~,down] = env_find(imit_im{j});
        imit_env{j} = [up down];
    end
    cnt = 1;
%     for m = 1:length(ntvid)
%         for n = 1:length(imitid)
% %             dtw_temp(cnt) = dtw(ntv_env{m}, imit_env{n});
% %             [cm(cnt), cSq] = DiscreteFrechetDist(ntv_env{m},imit_env{n});
% %             ssimval(cnt) = ssim(imit_im{n},ntv_im{m});
% %             euc(cnt) = sqrt(sum((imit_im{n}(:) - ntv_im{m}(:)) .^ 2));
%             euc(cnt) = sqrt(sum((imit_env{n} - ntv_env{m}) .^ 2));
%             
%             cnt = cnt+1;
%         end
%     end
    
%     R = corrcoef(group1,group2); % Pearson correlations. look into diagonal values. 
%     [A,B,r] = canoncorr(X,Y); % Cannonical correlations. A,B coefecient, r is the correlations.

%     dtw_dist(i) = mean(dtw_temp);
%     dft_dist(i) = mean(cm);
%     ssim_dist(i) = mean(ssimval);
%     euc_dist(i) = mean(euc);
    euc_dist_env(i) = mean(euc);
    
end

plot(euc_dist_env)
%% post observation

load('euc_dist_im.mat')
figure
plot(euc_dist)
hold on
plot(dft_dist)
xlabel('Class #')
ylabel('Distance')
legend('DTW','DFT')
th = zeros(1,110)+600;
[sorted, I] = sort(dtw_dist, 'ascend');

zz = dtw_dist(dtw_dist<600);















