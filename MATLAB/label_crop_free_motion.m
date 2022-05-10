clc; clear; close all;

impath = 'C:\Users\emrek\Desktop\microDoppler blake free seq\';
imlabelpath = [impath 'labels\microDoppler\'];
rdlabelpath = [impath 'labels\rangeDoppler\'];
% cropImPath = ['D:\110signOutput\' sub '\microDoppler\Cut\'];
% cropRDPath = ['D:\110signOutput\' sub '\rangeDoppler\Cut\'];

pattern = strcat(impath, '*.png');    % file pattern
files = dir(pattern);

if ~exist(imlabelpath, 'dir')
    mkdir(imlabelpath)
    mkdir(rdlabelpath)
end
I_MAX = length(files); % # of files in "files" 

% keynums = 1:110;
% keys = num2cell(keynums);
% values = {'water','iloveyou','you','yes','eat','ohisee','want','deaf','me','work',...
%     'book','sleep','teach','mother','thankyou','car','evening','tired','hello','ok',...
%     'this','letmesee','paper','home','friend','more','good','must','he','what',...
%     'today','hold','school','read','coffee','time','change','ready','better','father',...
%     'drink','tomorrow','see','nothing','my','hot','bed','why','soon','where',...
%     'shop','like','your','technology','bring','pet','please','help','one','have',...
%     'should','walk','dontlike','always','morning','fine','month','city','three','gas',...
%     'wrong','cook','doesntmatter','shoes','teacher','goahead','again','summon','week','maybe',...
%     'kitchen','breakfast','excited','go','money','night','tieup','can','licence','people',...
%     'table','winter','something','right','trilled','explanation','family','toilet','there','long',...
%     'knife','engineer','mountain','lawyer','hospital','health','earth','push','come','write'};
% map = containers.Map(keys,values);
 
m = 200;
n = 700;
dlgtitle = 'Input Class';
dims = [1 150];
c = newline;
for i = 13:I_MAX
    
    fig = fullfile(files(i).folder,files(i).name);
    fname = files(i).name(1:end-4);
    
    vidlabelname = strcat(rdlabelpath, fname,'.txt'); 
    imlabelname = strcat(imlabelpath, fname,'.txt'); 
    
    image = imread(fig);
    imlen = size(image,2);
    vidlen = 30*25;
    ratio = imlen/vidlen;
    
    y_vid = zeros(1,vidlen); % labels
    y_im = zeros(1,imlen);
    
    flag = 1;
    count = 1;
    
    figure(1)
    imshow(image)
    set(gcf, 'units','normalized','outerposition',[.1 .2 .7 .7]); % 8 8 

    while flag
%     for j = 1:length(seq)
        msg = strcat(['Processing File ', int2str(i),'/',int2str(I_MAX),...
        ' | File: ',files(i).name,' | ', num2str(count), '. Crop']);
        disp(msg)
        movegui('north')

        h = imrect(gca,[m*count*3/2 52 m n]);
        position = round(wait(h)); %[left to right, top to bottom, x length, y length]
        posvid = round([position(1)/ratio (position(1)+position(3))/ratio]);
        m = position(3);
        prompt = strcat(['File: ',fname,c,'j = ',num2str(count),' i = ',num2str(i),c,...
            '''s'': skip this file, ''x'': finish cropping:']);
        class{i,count} = newid(prompt,dlgtitle,dims);% inputdlg
        if string(class{i,count}) == 'x' || string(class{i,count}) == 's'
            break
        end
        delete(h); 
        y_vid(posvid(1):posvid(2)) = str2num(string(class{i,count}));
        y_vid = y_vid(1:vidlen); % make sure it doesn't go beyond the length
%         y_vid(posvid(1):posvid(2)) = str2num(class);
        y_im(position(1):position(1)+position(3)) = str2num(string(class{i,count}));
        y_im = y_im(1:imlen); % make sure it doesn't go beyond the length
%         y_im(position(1):position(1)+position(3)) = str2num(class);
        
%         cropColor = imcrop(image, position);
%         cropGray= imcrop(im_gray, position);
%         saveColor = strcat(cropImPath,fname, '_', map(str2num(string(class{i,count}))), '_',num2str(count), '.png');
%         saveColor = strcat(cropImPath,fname, '_', num2str(count), '_', class, '.png');
%         saveGray = strcat(cropImPath,fname,'_',num2str(count),'_',string(class{i,count}), '_gray.png');
%         imwrite(cropColor, saveColor);
%         imwrite(cropGray, saveGray);
        
%         cutVideo = VideoWriter(strcat(cropVidPath,fname, '_', num2str(count), '_', class, '.avi'));
%         cutVideo.FrameRate = fps;
%         
%         open(cutVideo);
%         for k = posvid(1):posvid(2)
%             vidFrames = read(v,k);
%             writeVideo(cutVideo,vidFrames)
%         end
%         close(cutVideo);
%         
        count = count+1;
%         if count >= 6
%             break
%         end
    end
%     if string(class{i,count-1}) == 's'
%             continue
%     end
    dlmwrite(vidlabelname, y_vid,'delimiter',' ');
    dlmwrite(imlabelname, y_im,'delimiter',' ');
    close all
end

