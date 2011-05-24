function [ start sumT ] = gridSum( q )
windowSize = 400
coarse = 20
alpha = 0.01

sumT = [];
sumQ = sum(q(1:windowSize, 2));
prev = sumQ;
sumT(1) = sumQ;
start = [];
start(1) = q(1, 1);
for i = 2:length(q) - windowSize +1
    sumQ = sumQ - q(i-1, 2) + q(i+windowSize-1, 2);
    sumT(i) = (1-alpha)*prev + alpha*sumQ;
    start(i) = q(i, 1);
    prev = sumQ;
end

%start = start / 10 / 3600;
sumT = sumT / windowSize;

start = start(1:coarse:length(start)); 
sumT = sumT(1:coarse:length(sumT));


end

