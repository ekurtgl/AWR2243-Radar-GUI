function [upper_env, lower_env]=env_up_low(fIn)
% clc; clear all; close all;
% fIn='D:\png_img\asl.png';
 im=im2double(rgb2gray(imread(fIn)));
 im2=imresize(im,[128 128]);
%img_matrix = im2double(rgb2gray(imread(fIn)));
img_matrix=im2;
img_matrix(img_matrix<0.0589) = 0;
total_pow = sum(img_matrix);
upper_lim = 0.98*total_pow;
central_lim = 0.5*total_pow;
lower_lim = 0.09*total_pow;
upper_env = zeros(1,size(img_matrix,2));
central_env = zeros(1,size(img_matrix,2));
lower_env = zeros(1,size(img_matrix,2));

Sum = 0;
[b,a]=butter(2,10/(250/2));
%% Upper Envelope
for t = 1:size(img_matrix,2)  
    for v = size(img_matrix,1):-1:1
        Sum = Sum + img_matrix(v,t);
        if Sum > upper_lim(t)
            Sum = 0;
            break
        end
    end
    upper_env(t) = v;
end
upper_env(upper_env<6) = max(upper_env);
upper_env=filtfilt(b,a,upper_env);

Sum=0;
%% Lower envelope
for t = 1:size(img_matrix,2)  
    for v = size(img_matrix,1):-1:1
        Sum = Sum + img_matrix(v,t);
        if Sum > lower_lim(t)
            Sum = 0;
            break
        end
    end
    lower_env(t) = v;
end
%lower_env(lower_env>120) = min(lower_env);
lower_env=filtfilt(b,a,lower_env);

%{
%% Central envelope
Sum=0;
for t = 1:size(img_matrix,2)  
    for v = size(img_matrix,1):-1:1
        Sum = Sum + img_matrix(v,t);
        if (Sum > central_lim(t))
         
                Sum = 0;
                break
            
        end
    end
    central_env(t) = v;
end
central_env=filtfilt(b,a,central_env);
figure; imshow(imread(fIn));hold on; plot(1*(upper_env),'m','LineWidth',2);hold on; plot(1*(lower_env),'r','LineWidth',2);hold on; plot(1*(central_env),'g','LineWidth',1)

%figure; imshow(imread(fIn));hold on; plot(1*(new_env),'m','LineWidth',2);hold on; plot(1*(new_env_high),'y','LineWidth',2);
Upper_velocity = pix_to_vel(upper_env);
Central_velocity = pix_to_vel(central_env);
Lower_velocity = pix_to_vel(lower_env);
time_axis=linspace(0,15,length(Upper_velocity));
figure;plot(time_axis,(Upper_velocity),'m','LineWidth',2);hold on;plot(time_axis,(Lower_velocity),'m','LineWidth',2);hold on;plot(time_axis,(Central_velocity),'g','LineWidth',1);
xlabel('Time (Sec)');ylabel('Torso velocity (M/S)');
%}

