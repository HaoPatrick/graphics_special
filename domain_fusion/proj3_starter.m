% starter script for project 3
DO_TOY = true;
DO_BLEND = false;
DO_MIXED  = false;
DO_COLOR2GRAY = false;

if DO_TOY 
    toyim = im2double(imread('../assets/poisson_blending/toy_problem.png')); 
    % im_out should be approximately the same as toyim
    im_out = toy_reconstruct(toyim);
    disp(['Error: ' num2str(sqrt(sum((toyim(:)-im_out(:)).^2)))])
end

if DO_BLEND
    % do a small one first, while debugging
    im_background = imresize(im2double(imread('../assets/poisson_blending/im2.JPG')), 0.25, 'bilinear');
    im_object = imresize(im2double(imread('../assets/poisson_blending/penguin-chick.jpeg')), 0.25, 'bilinear');

    % get source region mask from the user
    objmask = getMask(im_object);
    % align im_s and mask_s with im_background
    [im_s, mask_s] = alignSource(im_object, objmask, im_background);

    % blend
    im_blend = poisson_blend(im_s, mask_s, im_background);
    figure(3), hold off, imshow(im_blend)
end

if DO_MIXED
    % read images
    %...
    im_background = imresize(im2double(imread('../assets/poisson_blending/wall.jpg')),0.99,'bilinear');
    im_object= imresize(im2double(imread('../assets/poisson_blending/rainbow.jpg')),0.99,'bilinear');
    
    objmask=getMask(im_object);
    [im_s,mask_s]=alignSource(im_object, objmask, im_background);
    
    % blend
    im_blend = mixed_blend(im_s, mask_s, im_background);
    figure(3), hold off, imshow(im_blend);
end

if DO_COLOR2GRAY
    % also feel welcome to try this on some natural images and compare to rgb2gray
    im_rgb = im2double(imread('../assets/poisson_blending/colorBlindTest35.png'));
    im_gr = color2gray(im_rgb);
    figure(4), hold off, imagesc(im_gr), axis image, colormap gray
end
