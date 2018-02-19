function [ im_out ] = color2gray( im )
[imh, imw, ~] = size(im);
num_pixels = imh * imw;
im2var = zeros(imh, imw);
im2var(1:num_pixels) = 1:num_pixels;

num_equations = 2*num_pixels + 1;
A = sparse([],[],[],num_equations, num_pixels,num_pixels*2);
b = zeros(num_equations, 1);

e = 1;
for y = 1:imh
    for x = 1:imw
        if x~=imw
            A(e, im2var(y, x+1)) = 1;
            A(e, im2var(y, x)) = -1;
            b(e) =find_max_abs( im(y, x+1, 1)-im(y,x,1), im(y, x+1, 2)-im(y,x,2),im(y, x+1, 3)-im(y,x,3));
            e = e+1;
        end
        if y~=imh
            A(e, im2var(y+1, x)) = 1;
            A(e, im2var(y, x)) = -1;
            b(e) =find_max_abs( im(y+1, x, 1)-im(y,x,1), im(y+1, x, 2)-im(y,x,2),im(y+1, x, 3)-im(y,x,3));
            e = e+1;
        end
    end
end
A(e, im2var(1,1)) = 1;
b(e) = im(1,1,1);

v = A\b;
im_out = reshape(v, [imh imw]);
imshow(im_out);
%imshow(rgb2gray(im));
end

function [d] = find_max_abs(a,b,c)
if abs(a)>abs(b) && abs(a) >abs(c)
    d=a;
elseif abs(b)>abs(a) && abs(b)>abs(c)
        d=b;
else
    d=c;
end
end