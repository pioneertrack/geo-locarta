//
//  DetailsViewController.m
//  BenchMark
//
//  Created by gisdev on 12/21/17.
//  Copyright © 2017 igis.me. All rights reserved.
//

#import "DetailsViewController.h"

@interface DetailsViewController ()
@property(nonatomic,strong)UITableView * tableView;
@property(nonatomic,strong)NSArray * keys;
@end

@implementation DetailsViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view.
    self.tableView = [[UITableView alloc] initWithFrame:self.view.frame style:(UITableViewStyleGrouped)];
    self.tableView.delegate = self;
    self.tableView.dataSource = self;
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    [self.view addSubview:self.tableView];
    _keys = [self.data allKeys];
    self.title=@"details";
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return [_keys count];
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath
{
    CGFloat h=44;
    
    return h;
}
- (UIView *)tableView:(UITableView *)tableView viewForFooterInSection:(NSInteger)section
{
    
    return nil;
}
- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    UITableViewCell * cell =nil;
    cell = [tableView dequeueReusableCellWithIdentifier:@"UITableViewCell"];
    if (!cell) {
        cell = [[UITableViewCell alloc] initWithStyle:UITableViewCellStyleValue1 reuseIdentifier:@"UITableViewCell"];
    }
    
    cell.textLabel.text=[_keys objectAtIndex:indexPath.row];
    
    id v=[self.data objectForKey:[_keys objectAtIndex:indexPath.row]];
    if ([v isKindOfClass:[NSString class]]) {
        cell.detailTextLabel.text = v;
    }
    else
    {
        cell.detailTextLabel.text = [v stringValue];
    }
    
    
    return cell;
}

@end
