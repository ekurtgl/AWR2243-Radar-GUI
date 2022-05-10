clc; clear; close all;

seq = '3'; % sequence

vidpath = ['D:\COVID19 Sequential\out\seq',seq,'\rangedopp\'];
impath = ['D:\COVID19 Sequential\out\seq',seq,'\mdopp\'];

vidlabelpath = ['D:\COVID19 Sequential\out\seq',seq,'\rangedopp\labels\'];
imlabelpath = ['D:\COVID19 Sequential\out\seq',seq,'\mdopp\labels\'];

cropImPath = ['D:\COVID19 Sequential\out\seq',seq,'\mdopp\Cropped\'];
cropVidPath = ['D:\COVID19 Sequential\out\seq',seq,'\rangedopp\Cropped\'];

pattern = strcat(impath, '*.fig');    % file pattern
files = dir(pattern);

pattern2 = strcat(vidpath, '*.avi');    % file pattern
files2 = dir(pattern2);

I_MAX = numel(files); % # of files in "files" 

m = 400;
n = 1500;
dlgtitle = 'Input Class';
dims = [1 150];
c = newline;
for i = 1:I_MAX
    
    fig = fullfile(files(i).folder,files(i).name);
    fname = files(i).name(1:end-4);
    vid = fullfile(files2(i).folder,[fname '.avi']);
    v = VideoReader(vid);
    fps = v.FrameRate;
    duration = v.Duration; % sec
    num_frame = v.Numberofframe;
    
    
    vidlabelname = strcat(vidlabelpath, fname,'.txt'); 
    imlabelname = strcat(imlabelpath, fname,'.txt'); 
    
    openfig(fig);
    set(gca,'Ydir','normal')
    image = frame2im(getframe(gca));
    colormap(gray)
    im_gray = frame2im(getframe(gca));

    imlen = size(image,2);
    vidlen = num_frame;
    ratio = imlen/vidlen;
    
    y_vid = zeros(1,num_frame); % labels
    y_im = zeros(1,imlen);
    
    flag = 1;
    count = 1;
    
    figure(1)
    imshow(image)
    set(gcf, 'units','normalized','outerposition',[.1 .2 .7 .7]); % 8 8 

    while flag
        msg = strcat(['Processing File ', int2str(i),'/',int2str(I_MAX),...
        ' | File: ',files(i).name,' | ', num2str(count), '. Crop']);
        disp(msg)
        movegui('north')

        h = imrect(gca,[m/2*count 23 m n]);
        position = round(wait(h)); %[left to right, top to bottom, x length, y length]
        posvid = round([position(1)/ratio (position(1)+position(3))/ratio]);
        prompt = strcat(['File: ',fname,c,'j = ',num2str(count),' i = ',num2str(i),c,'0 no move, ' ...
            '1 walk, 2 sit, 3 stand, 4 fold, 5 iron, 6 YOU, 7 HELLO, 8 CAR, 9 PUSH, ''x'' exit:']);
        class{i,count} = newid(prompt,dlgtitle,dims);% inputdlg
        if string(class{i,count}) == 'x'
            break
        end
        delete(h); 
        y_vid(posvid(1):posvid(2)) = str2num(string(class{i,count}));
        y_im(position(1):position(1)+position(3)) = str2num(string(class{i,count}));
        
        cropColor = imcrop(image, position);
        cropGray= imcrop(im_gray, position);
        saveColor = strcat(cropImPath,fname,'_',num2str(count),'_', string(class{i,count}), '.png');
        saveGray = strcat(cropImPath,fname,'_',num2str(count),'_',string(class{i,count}), '_gray.png');
        imwrite(cropColor, saveColor);
        imwrite(cropGray, saveGray);
        
        cutVideo = VideoWriter(strcat(cropVidPath,fname,'_',num2str(count),'_',string(class{i,count}),'.avi'));
        cutVideo.FrameRate = fps;
        
        open(cutVideo);
        for k = posvid(1):posvid(2)
            vidFrames = read(v,k);
            writeVideo(cutVideo,vidFrames)
        end
        close(cutVideo);
        
        count = count+1;
    end
    dlmwrite(vidlabelname, y_vid,'delimiter',' ');
    dlmwrite(imlabelname, y_im,'delimiter',' ');
    close all
end

