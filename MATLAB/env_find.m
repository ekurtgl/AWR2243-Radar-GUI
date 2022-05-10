function [upper_env, central_env, lower_env] = env_find(fIn)

img_matrix = im2double(rgb2gray(fIn));
img_matrix=img_matrix(5:end-4,:);

%img_matrix=(img_matrix-0.5)/.5;
img_matrix(img_matrix<0.0589) = 0;
%img_matrix(img_matrix<-0.88) = 0;
total_pow = sum(img_matrix);
upper_lim = 0.95*total_pow; %.97
central_lim = 0.5*total_pow;
lower_lim = 0.003*total_pow; %.03

upper_env = zeros(1,size(img_matrix,2));
central_env = zeros(1,size(img_matrix,2));
lower_env = zeros(1,size(img_matrix,2));

Sum = 0;
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
lower_env(lower_env<6) = max(upper_env);
%% Central envelope
for t = 1:size(img_matrix,2)  
    for v = size(img_matrix,1):-1:1
        Sum = Sum + img_matrix(v,t);
        if Sum > central_lim(t)
            Sum = 0;
            break
        end
    end
    central_env(t) = v;
end
central_env(central_env<6) = max(upper_env);
%% Features
% f(1) = min(upper_env); %  minimum value of the upper envelope
% f(2) = max(upper_env); %  maximum value of the upper envelope
% f(3) = mean(upper_env); %  meanvalue of the upper envelope
% 
% f(4) = min(lower_env); %  minimum value of the lower envelope
% f(5) = max(lower_env); %  maximum value of the lower envelope
% f(6) = mean(lower_env); %  meanvalue of the lower envelope
% 
% f(7) = abs(f(3)-f(6)); % difference between upper and lower envelope averages
% figure(1);
% imshow(img_matrix)
% hold on
% p1 = plot(upper_env,'g','LineWidth',2);
% p2 = plot(lower_env,'r','LineWidth',2);
% p3 = plot(central_env,'b','LineWidth',2);
% legend([p1,p2,p3], 'Upper Env','Lower Env','Central Env');
end