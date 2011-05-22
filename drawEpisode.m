%load no_transfer.csv
%load transfer.csv
%
fileList = {
            'reward_sarsa',
            'reward_pun0',
            %'reward_pun2',
            'reward_pun5',
            'reward_pun30',
            'reward_pun50',
            %'reward_pun50',
            %'reward_pun105'
}
%fileList = {'RRL_test_3333__1_1__3', 'RRL_test_2000__2_1__5', 'RRL_test_2000__1_2__5'}
plotSpec = {'r-', 'g-', 'b-', 'r.-', 'g.-', 'r-+', 'g-+', 'b-+'}

for i = 1:length(fileList)
    name = char(fileList(i))
    filename = [name '.csv']
    load(filename)
    eval(['data = ' name ';'])
    q = [data(:, 1) data(:, 3)];
    [start sumT] = gridSum(q);
    plot(start, sumT, char(plotSpec(i)))
    hold on
end
xlabel('# steps')
ylabel('reward per episode')
legend( 'reward sarsa', 'reward pun0', 'reward pun2', 'reward pun5', 'reward pun10', 'reward pun 50', 'reward pun 105')
%load('conv.csv')
%SARSA = conv;
%load('RRL_conv.csv')
%RRL = RRL_conv;
%avg = computeAvg(data, episodeNum);
%plot(X, avg)
%hold on
%avg = computeAvg(SARSA, episodeNum);
%plot(X, avg, ':')



%data = load('reward_pun5.csv');
%load 4vs3tran.csv

 %hold on;
 
%data = X4vs3no;
%q = data(:, 4);
%[start sumT] = winsum(q);
 %plot(start, sumT, 'r.-')
%axis([0 18 8 15])
