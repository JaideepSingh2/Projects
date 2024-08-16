function [output dx_best dy_best] = Im_Align_Crop(f,g) %align frame f to frame g and crop f down to size of g

search_width = 3; %how many pixels over which to search for appropriate shift

[height, width, channels] = size(f);
imdim = 14;
ypos = ceil(height/2); 
xpos = ceil(width/2); 
MSE_min = 100000; 
for dx = -search_width:search_width
    for dy = -search_width:search_width
        A = [1 0 dx; 0 1 dy; 0 0 1]; 
        tform = maketform('affine',A.'); 
        frameTform = imtransform(f, tform, 'bilinear', 'Xdata', [1 width], 'YData', [1 height], 'FillValues', zeros(channels,1));
        %Crop frameTform
        if size(frameTform,1) ~= 30 | size(frameTform,2) ~= 30
            frameTform = frameTform(ypos-(imdim+1):ypos+imdim,xpos-(imdim+1):xpos+imdim);
        end
        %calculate MSE between shifted image and g
        MSE = sum(sum(sum((g - frameTform).^2))) / (height*width*channels); 
        if (MSE < MSE_min)
            MSE_min = MSE;
            dx_best = dx;
            dy_best = dy;
        end
    end
end

%Compute best alignment of f to g using dx_best and dy_best
A = [1 0 dx_best; 0 1 dy_best; 0 0 1]; 
%A = [1 0 0; 0 1 0; 0 0 1]; 
tform = maketform('affine',A.'); 
[height, width, channels] = size(f); 
output = imtransform(f, tform, 'bilinear', 'Xdata', [1 width], 'YData', [1 height], 'FillValues', zeros(channels,1));
%Crop output
if size(output,1) ~= 30 | size(output,2) ~= 30
    output = output(ypos-(imdim+1):ypos+imdim,xpos-(imdim+1):xpos+imdim);
end
