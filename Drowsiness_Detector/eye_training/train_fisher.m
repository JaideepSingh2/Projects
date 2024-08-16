clc
clear all
close all

% Specify directory names for training data 
open_name = 'fisher_data/open/';
close_name = 'fisher_data/close/';

%% Rest of Program
% Directories 
open_training_dir = dir(open_name); 
close_training_dir = dir(close_name);

%% Part A: Align and crop images 
open_training = []; 

bad_data_count = 0; 
%v = VideoWriter('eyes_aligned.avi'); 
%v.FrameRate = 4; 
%open(v); 
for k = 3:length(open_training_dir)
    ind = k-2 - bad_data_count; 
    name = strcat('./',open_name, open_training_dir(k).name);
    Im = rgb2gray(im2double(imread(name)));
    
    %Make sure image is large enough to be considered
    [height width depth] = size(Im);
    if (height < 30) | (width < 30)
        'too small'
        bad_data_count = bad_data_count + 1; 
        continue 
    end
    
    %Apply adaptive histogram equalization 
    Im = histeq(Im,256); 
    
    %Perform image alignment and crop
    if ind == 1 %don't align 
        %Crop image to 30x30 pixels, around the center pixel 
        %Important to neglect boundary effects from alignment, annd for
        %calculation of mean eye
        imdim = 14;
        ypos = ceil(height/2); 
        xpos = ceil(width/2); 
        Im = Im(ypos-(imdim+1):ypos+imdim,xpos-(imdim+1):xpos+imdim);
        Im1_open = Im;
        
    else 
        [Im,dx_best,dy_best] = Im_Align_Crop(Im,Im1_open); 
    end
    
    %Remember Im for later
    imshow(Im);
    %writeVideo(v,Im); 
    open_training(:,:,ind) = Im;
end
%close(v); 

close_training = []; 

bad_data_count = 0; 
for k = 3:length(close_training_dir)
    ind = k-2 - bad_data_count; 
    name = strcat('./',close_name, close_training_dir(k).name);
    Im = im2double(imread(name));
    
    %Make sure image is large enough to be considered
    [height width depth] = size(Im);
    if (height < 30) | (width < 30)
        'too small'
        bad_data_count = bad_data_count + 1; 
        continue 
    end
    
    %Apply adaptive histogram equalization 
    Im = histeq(Im,256); 
    
    %Perform image alignment and crop
    if ind == 1 %don't align 
        %Crop image to 30x30 pixels, around the center pixel 
        %Important to neglect boundary effects from alignment, annd for
        %calculation of mean eye
        imdim = 14;
        ypos = ceil(height/2); 
        xpos = ceil(width/2); 
        Im = Im(ypos-(imdim+1):ypos+imdim,xpos-(imdim+1):xpos+imdim);
        Im1_close = Im;
    else 
        [Im,dx_best,dy_best] = Im_Align_Crop(Im,Im1_close); 
    end
    
    %Remember Im for later
    imshow(Im);
    close_training(:,:,ind) = Im;
end

training = cat(3,open_training,close_training);
meaneye = mean(training,3); 

%% Part A continued: Perform alignment again, with meaneye obtained above 
open_training = []; 

bad_data_count = 0; 
for k = 3:length(open_training_dir)
    ind = k-2 - bad_data_count; 
    name = strcat('./', open_name, open_training_dir(k).name);
    Im = rgb2gray(im2double(imread(name)));
    
    %Make sure image is large enough to be considered
    [height width depth] = size(Im);
    if (height < 30) | (width < 30)
        'too small'
        bad_data_count = bad_data_count + 1; 
        continue 
    end
    
    %Apply adaptive histogram equalization 
    Im = histeq(Im,256); 
    
    %Perform image alignment and crop
    [Im,dx_best,dy_best] = Im_Align_Crop(Im,meaneye); 
        
    %Remember Im for later
    imshow(Im);
    open_training(:,:,ind) = Im;
end

close_training = []; 

bad_data_count = 0; 
for k = 3:length(close_training_dir)
    ind = k-2 - bad_data_count; 
    name = strcat('./', close_name, close_training_dir(k).name);
    Im = im2double(imread(name));
    
    %Make sure image is large enough to be considered
    [height width depth] = size(Im);
    if (height < 30) | (width < 30)
        'too small'
        bad_data_count = bad_data_count + 1; 
        continue 
    end
    
    %Apply adaptive histogram equalization 
    Im = histeq(Im,256); 
    
    [Im,dx_best,dy_best] = Im_Align_Crop(Im,meaneye); 
    
    %Remember Im for later
    imshow(Im);
    close_training(:,:,ind) = Im;
end

%% Part B: Compute top 10 eigenfaces of training images 
clc
close all

training = cat(3,open_training,close_training);
meaneye = mean(training,3); 
[height width depth] = size(training); 
%Mean remove the training images 
for i = 1:size(training,3)
    training(:,:,i) = training(:,:,i) - meaneye; 
end

%reshape so that images are vectors 
S = reshape(training, [], size(training,3)); 

%Compute eigenimages
SHS = S'*S; %LxL
[eigenvectors eigenvalues] = eig(SHS); 
[d ind] = sort(diag(eigenvalues),'descend');

eigeneyes = []; 
figure();
for i = 1:100
    vi = eigenvectors(:,ind(i));
    eye_i = S * -vi;
    eye_i = reshape(eye_i,height, width);
    eye_i = eye_i / norm(eye_i,2);
    eigeneyes(:,:,i) = eye_i; 
    if (i<=10)
        subplot(5,2,i); imshow(eye_i, [min(min(eye_i)) max(max(eye_i))]); 
    end
end

%% Part C: Compute Fisher Faces 
eyeProjections = [];
for i = 1:size(training,3)
    proj = []; 
    for j = 1:100
        proj = [proj; sum(sum(training(:,:,i) .* eigeneyes(:,:,j)))];
    end
    eyeProjections = [eyeProjections proj]; 
end

%Compute between class scatter matrix 
Class1 = eyeProjections(:,1:size(open_training,3));
Class2 = eyeProjections(:,size(open_training,3)+1:end);

u1 = mean(Class1,2); 
u2 = mean(Class2,2); 
u = mean(eyeProjections,2);

RB = 67*(u1-u)*(u1-u)' + 153*(u2-u)*(u2-u)';

%Compute within class scatter matrix 
RW = zeros(100,100); 

for i = 1:size(open_training,3)
    RW = RW + (Class1(:,i)-u1) * (Class1(:,i)-u1)'; 
end

for i = 1:size(close_training,3)
    RW = RW + (Class2(:,i)-u2) * (Class2(:,i)-u2)'; 
end

%Compute eigenvectors from scatter matrices
[eigenvectors eigenvalues] = eig(RB,RW); 

%Multiply these eigenvectors by eigenfaces to get fisherfaces
fishereyes = reshape(eigeneyes,30*30,100) * eigenvectors;
fishereyes = reshape(fishereyes,30,30,100);

%% Part D Fisherface Performance
eye = fishereyes(:,:,1); %fisherface 1
eye = eye ./ norm(eye,2); 

%Project training images onto face10 to get histograms 
score = [];
for i = 1:size(training,3)
    score = [score sum(sum(training(:,:,i) .* eye))]; 
end
score_open = score(1:size(open_training,3));
score_close = score(size(open_training,3)+1:end);

open_hist = hist(score_open, [-5:.25:5]);
close_hist = hist(score_close, [-5:.25:5]);

figure(); stem([-5:.25:5],open_hist);
hold on; stem([-5:.25:5], close_hist); 
legend('open','close');

