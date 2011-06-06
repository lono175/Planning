close all
%load no_transfer.csv
%load transfer.csv
%
fileList = {
            'reward_sarsa',
            'reward_pun0',
            %'reward_pun2',
            'reward_pun5',
            %'reward_pun10',
            %'reward_pun20',
            %'reward_pun50',
            'reward_pun60',
            'reward_RORDQ'
            %'reward_pun105'
}
%fileList = {'RRL_test_3333__1_1__3', 'RRL_test_2000__2_1__5', 'RRL_test_2000__1_2__5'}
%plotSpec = {'b.-', 'm--', 'r.-', 'k-', 'g--', 'r-+', 'g-+', 'b-+'}
plotSpec = {'--', '-', '-', '-', '--', '-+', '-+', '-+'}

colorSpec = {[0 1 0], [0 0 1], [0.75 0 0], [0 0 0], [1 0 1]}
for i = 1:length(fileList)
    name = char(fileList(i))
    filename = [name '.csv']
    load(filename)
    eval(['data = ' name ';'])
    q = [data(:, 1) data(:, 3)];
    [start sumT] = gridSum(q);
    plot(start/100000, sumT, char(plotSpec(i)), 'LineWidth', 3, 'Color', colorSpec{i})
    hold on
end
axis([0, 4, -160, -10])
xlabel('Number of steps (100,000s)')
ylabel('Reward per episode')
%legend( 'SARSA', 'Model+HORDQ(0)', 'Model+HORDQ(5)', 'Model+HORDQ(10)', 'Model+HORDQ(20)', 'Model+HORDQ(50)', 'Model+HORDQ(60)', 'Model+MaxQ')
legend( 'SARSA(0)', 'Model+HORDQ(0)', 'Model+HORDQ(5)',  'Model+HORDQ(60)', 'Model+MAXQ-Q', 'location', 'best')
%h_legend = legend( 'SARSA(0)', 'Random+HORDQ(0)', 'Random+HORDQ(5)',  'Random+HORDQ(60)', 'Random+MAXQ-Q', 'location', 'best')

h_xlabel = get(gca,'XLabel');
set(h_xlabel,'FontSize',18);
h_ylabel = get(gca,'YLabel');
set(h_ylabel,'FontSize',18);
%set(gcf,'Units','normal')
%set(gca,'Position',[0 0 1 1])

%set(h_legend,'FontSize',14);


%legend( 'Sarsa(0)', 'Random+HORDQ(0)', 'Random+HORDQ(5)',  'Random+HORDQ(60)', 'Random+MAXQ')
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
