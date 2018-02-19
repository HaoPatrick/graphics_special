function [ im_blend ] = poisson_blend( im, mask, im_bg )
%POISSONBLEND

[bgh, bgw, ~] = size(im_bg);

num_bg_pixels = bgh * bgw;
im2var = zeros(bgh, bgw);
im2var(1:num_bg_pixels) = 1:num_bg_pixels;

v_rgb = {1,2,3};
sparse_count=0;
for j = 1:bgh
    for i = 1:bgw
        if mask(j,i)==0
            sparse_count=sparse_count+1;
            continue;
        end
        sparse_count=sparse_count+mask(j-1, i)+mask(j+1, i)+mask(j, i-1)+mask(j, i+1)+1;
    end
end

for c = 1:3
    index_i = [];
    index_j = [];
    value_k = [];
    b = zeros(num_bg_pixels, 1);
    
    e = 1;
    for j = 1:bgh
        for i = 1:bgw
            if mask(j,i)==0
                index_i = [index_i e];
                index_j = [index_j im2var(j,i)];
                value_k = [value_k 1];
                
                b(e) = im_bg(j, i, c);
                e = e + 1;
                continue;
            end
            if mask(j-1, i)==1
                index_i = [index_i e];
                index_j = [index_j im2var(j-1,i)];
                value_k = [value_k -1];
            end
            if mask(j+1, i)==1
                index_i = [index_i e];
                index_j = [index_j im2var(j+1,i)];
                value_k = [value_k -1];
            end
            if mask(j, i-1)
                index_i = [index_i e];
                index_j = [index_j im2var(j,i-1)];
                value_k = [value_k -1];
            end
            if mask(j, i+1)
                index_i = [index_i e];
                index_j = [index_j im2var(j,i+1)];
                value_k = [value_k -1];
            end
            
            % laplacian operator
            index_i = [index_i e];
            index_j = [index_j im2var(j,i)];
            value_k = [value_k 4];

            b(e) = 0;
            b(e) = b(e) + im(j,i,c) - im(j-1,i,c);
            b(e) = b(e) + im(j,i,c) - im(j+1,i,c);
            b(e) = b(e) + im(j,i,c) - im(j,i+1,c);
            b(e) = b(e) + im(j,i,c) - im(j,i-1,c);
            
            if mask(j-1,i)==0
                b(e) = b(e) + im_bg(j-1,i,c);
            end
            if mask(j+1,i)==0
                b(e) = b(e) + im_bg(j+1,i,c);
            end
            if mask(j,i+1)==0
                b(e) = b(e) + im_bg(j,i+1,c);
            end
            if mask(j,i-1)==0
                b(e) = b(e) + im_bg(j,i-1,c);
            end
            e = e + 1;
        end
    end
    
    A = sparse(index_i, index_j, value_k, num_bg_pixels, num_bg_pixels);
    v_rgb{c} = A\b;
end
disp(size(index_i));
disp(sparse_count);

for c = 1:3
    im_blend(:,:,c) = reshape(v_rgb{c}, [bgh bgw]);
end

end