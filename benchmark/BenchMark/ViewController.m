//
//  ViewController.m
//  BenchMark
//
//  Created by gisdev on 12/15/17.
//  Copyright © 2017 igis.me. All rights reserved.
//

#import "ViewController.h"
#import <AFNetworking.h>
#import "DetailsViewController.h"
#import "MyCustomPointAnnotation.h"
#import <MapBox/NSExpression+MGLAdditions.h>
@import Mapbox;
@interface ViewController ()
@property(nonatomic,strong)MGLMapView *mapView;
@property(nonatomic,strong)id<MGLAnnotation>  anno;
@property(nonatomic,strong) MGLSymbolStyleLayer *pointStyleLayer;
@property(nonatomic,strong) MGLSymbolStyleLayer *qld4StyleLayer;

@end

@implementation ViewController
/*
-(void)fetchDataByID:(NSInteger)oId result:(void (^)(NSDictionary * _Nonnull))result
{
    NSString *url =[NSString stringWithFormat:@"http://49.4.7.32/pollsurvey/api/v1/gis_area/get_act_by_object_id?accessToken=cf741b47dd4d049a61599fcfa0ceac86&objectId=%ld", oId];
    [[AFHTTPSessionManager manager] GET:url parameters:nil progress:^(NSProgress * _Nonnull downloadProgress) {
        
    } success:^(NSURLSessionDataTask * _Nonnull task, id  _Nullable responseObject) {
        result(responseObject);
    } failure:^(NSURLSessionDataTask * _Nullable task, NSError * _Nonnull error) {
        
    }];
}
-(void)fetchNDataByX:(double)x y:(double)y result:(void (^)(NSDictionary * _Nonnull))result
{
    NSString *url =[NSString stringWithFormat:@"http://49.4.7.32/pollsurvey/api/v1/gis_area/act_nearest_list_by_location?num=15&lon=%lf&lat=%lf&accessToken=cf741b47dd4d049a61599fcfa0ceac86", x,y];
    [[AFHTTPSessionManager manager] GET:url parameters:nil progress:^(NSProgress * _Nonnull downloadProgress) {
        
    } success:^(NSURLSessionDataTask * _Nonnull task, id  _Nullable responseObject) {
        result(responseObject);
    } failure:^(NSURLSessionDataTask * _Nullable task, NSError * _Nonnull error) {
        
    }];
}
 */
- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
  /*
    NSData * data=[NSData dataWithContentsOfURL:[NSURL URLWithString:@"https://api.mapbox.com/styles/v1/benchmrk/cjgejcwla001c2sob79dqao7j?access_token=pk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2o1OWhoY2RrMDh2OTMycXFzOW9wNnNzbCJ9._M9OjLsK1TBHSxAwTmksaQ#9.5/-37.817162/144.966583/0"]];
    NSDictionary *json = [NSJSONSerialization JSONObjectWithData:data options:kNilOptions error:nil];
    NSData * data2=[NSData dataWithContentsOfURL:[NSURL URLWithString:@"https://api.mapbox.com/styles/v1/mapbox/streets-v10?access_token=pk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2o1OWhoY2RrMDh2OTMycXFzOW9wNnNzbCJ9._M9OjLsK1TBHSxAwTmksaQ"]];
    NSData * dataSatellite=[NSData dataWithContentsOfURL:[NSURL URLWithString:@"https://api.mapbox.com/styles/v1/mapbox/satellite-v9?access_token=pk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2o1OWhoY2RrMDh2OTMycXFzOW9wNnNzbCJ9._M9OjLsK1TBHSxAwTmksaQ"]];
    NSData * dataSatelliteStreet=[NSData dataWithContentsOfURL:[NSURL URLWithString:@"https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v10?access_token=pk.eyJ1IjoiYmVuY2htcmsiLCJhIjoiY2o1OWhoY2RrMDh2OTMycXFzOW9wNnNzbCJ9._M9OjLsK1TBHSxAwTmksaQ"]];
    NSDictionary *json2 = [NSJSONSerialization JSONObjectWithData:data2 options:kNilOptions error:nil];
    NSDictionary *jsonSatellite = [NSJSONSerialization JSONObjectWithData:dataSatellite options:kNilOptions error:nil];
    NSDictionary *jsonSatelliteStreet = [NSJSONSerialization JSONObjectWithData:dataSatelliteStreet options:kNilOptions error:nil];
    
    NSMutableDictionary *mergeJson = [[NSMutableDictionary alloc] initWithDictionary:[json2 copy] copyItems:YES];
    NSString * url =json[@"sources"][@"composite"][@"url"];
    url=[url stringByReplacingOccurrencesOfString:@"mapbox://" withString:@""];
    NSString * url2 =json2[@"sources"][@"composite"][@"url"];
    NSString *mergeUrl =[NSString stringWithFormat:@"%@,%@",url2,url];
    NSMutableDictionary*dictComposite= [mergeJson[@"sources"][@"composite"] mutableCopy];
    [dictComposite setValue:mergeUrl forKey:@"url"];
    NSMutableDictionary*dictSource =[mergeJson[@"sources"] mutableCopy];
    [dictSource setObject:dictComposite forKey:@"composite"];
    mergeJson[@"sources"]=dictSource;
    NSArray *layers=json2[@"layers"];
    NSMutableArray *mergeLayers =[[NSMutableArray alloc] initWithArray:layers];
    [mergeLayers addObjectsFromArray:json[@"layers"]];
    mergeJson[@"layers"]=mergeLayers;
    NSString* filePath = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) objectAtIndex:0];
    NSString* fileName = @"street.json";
    NSString* fileAtPath = [filePath stringByAppendingPathComponent:fileName];
    if (![[NSFileManager defaultManager] fileExistsAtPath:fileAtPath]) {
        [[NSFileManager defaultManager] createFileAtPath:fileAtPath contents:nil attributes:nil];
    }
    NSData *serialzedData=[NSJSONSerialization dataWithJSONObject:mergeJson options:0 error:nil];
    
    NSString *strData = [[NSString alloc] initWithBytes:[serialzedData bytes] length:[serialzedData length] encoding:NSUTF8StringEncoding];
    
    // The main act...
    [[strData dataUsingEncoding:NSUTF8StringEncoding] writeToFile:fileAtPath atomically:NO];

    
    NSMutableDictionary *mergeJsonSatellite = [[NSMutableDictionary alloc] initWithDictionary:[jsonSatellite copy] copyItems:YES];

    NSString * urlSatellite =jsonSatellite[@"sources"][@"composite"][@"url"];
   NSMutableDictionary*dictCompositeSatellite =[json[@"sources"][@"composite"] mutableCopy];
 //   NSString *mergeUrlSatellite =[NSString stringWithFormat:@"%@,%@",urlSatellite,url];
  //  NSMutableDictionary*dictCompositeDark= [mergeJsonDark[@"sources"][@"composite"] mutableCopy];
  //  [dictCompositeDark setValue:mergeUrldark forKey:@"url"];
    NSMutableDictionary*dictSourceSatellite =[mergeJsonSatellite[@"sources"] mutableCopy];
    [dictSourceSatellite setObject:dictCompositeSatellite forKey:@"composite"];
    mergeJsonSatellite[@"sources"]=dictSourceSatellite;
 
    NSMutableArray *mergeLayersSatellite =[[NSMutableArray alloc] initWithArray:jsonSatellite[@"layers"]];
    [mergeLayersSatellite addObjectsFromArray:json[@"layers"]];
    mergeJsonSatellite[@"layers"]=mergeLayersSatellite;

    fileName = @"Satellite.json";
    fileAtPath = [filePath stringByAppendingPathComponent:fileName];
    if (![[NSFileManager defaultManager] fileExistsAtPath:fileAtPath]) {
        [[NSFileManager defaultManager] createFileAtPath:fileAtPath contents:nil attributes:nil];
    }
    serialzedData=[NSJSONSerialization dataWithJSONObject:mergeJsonSatellite options:0 error:nil];
    
    strData = [[NSString alloc] initWithBytes:[serialzedData bytes] length:[serialzedData length] encoding:NSUTF8StringEncoding];
    
    // The main act...
    [[strData dataUsingEncoding:NSUTF8StringEncoding] writeToFile:fileAtPath atomically:NO];
    
    NSMutableDictionary *mergeJsonSatelliteStreet = [[NSMutableDictionary alloc] initWithDictionary:[jsonSatelliteStreet copy] copyItems:YES];
    
    NSString * urlSatelliteStreet =jsonSatelliteStreet[@"sources"][@"composite"][@"url"];
    NSString *mergeUrlSatelliteStreet =[NSString stringWithFormat:@"%@,%@",urlSatelliteStreet,url];
    NSMutableDictionary*dictCompositeSatelliteStreet= [mergeJsonSatelliteStreet[@"sources"][@"composite"] mutableCopy];
    [dictCompositeSatelliteStreet setValue:mergeUrlSatelliteStreet forKey:@"url"];
    NSMutableDictionary*dictSourceSatelliteStreet =[mergeJsonSatelliteStreet[@"sources"] mutableCopy];
    [dictSourceSatelliteStreet setObject:dictCompositeSatelliteStreet forKey:@"composite"];
    mergeJsonSatelliteStreet[@"sources"]=dictSourceSatelliteStreet;
    
    NSMutableArray *mergeLayersSatelliteStreet =[[NSMutableArray alloc] initWithArray:jsonSatelliteStreet[@"layers"]];
    [mergeLayersSatelliteStreet addObjectsFromArray:json[@"layers"]];
    mergeJsonSatelliteStreet[@"layers"]=mergeLayersSatelliteStreet;
    
    fileName = @"SatelliteStreet.json";
    fileAtPath = [filePath stringByAppendingPathComponent:fileName];
    if (![[NSFileManager defaultManager] fileExistsAtPath:fileAtPath]) {
        [[NSFileManager defaultManager] createFileAtPath:fileAtPath contents:nil attributes:nil];
    }
    serialzedData=[NSJSONSerialization dataWithJSONObject:mergeJsonSatelliteStreet options:0 error:nil];
    
    strData = [[NSString alloc] initWithBytes:[serialzedData bytes] length:[serialzedData length] encoding:NSUTF8StringEncoding];
    
    // The main act...
    [[strData dataUsingEncoding:NSUTF8StringEncoding] writeToFile:fileAtPath atomically:NO];

    
    */
   // NSURL *styleURL = [NSURL URLWithString:@"mapbox://styles/benchmrk/cjp0h3yj308nc2qphdvmy466e"];
    NSURL *styleURL = [NSURL URLWithString:@"mapbox://styles/benchmrk/cjp0h3yj308nc2qphdvmy466e"];
   
//    NSURL * styleURL= [MGLStyle streetsStyleURL];
    MGLMapView *mapView = [[MGLMapView alloc] initWithFrame:self.view.bounds
                                                   styleURL:styleURL];
//    MGLMapView *mapView = [[MGLMapView alloc] initWithFrame:self.view.bounds
//                                               styleURL:[NSURL fileURLWithPath:fileAtPath]];
    self.mapView = mapView;
    mapView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    
    // Set the map’s center coordinate and zoom level.
    //, south=-27 -28.27/153.12
   
    
    [self.view addSubview:mapView];
    self.mapView.delegate=self;
    UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(handleTap:)];
    gesture.delegate = self;
    gesture.numberOfTapsRequired = 1;
    [mapView addGestureRecognizer:gesture];
   
    /*
    UISegmentedControl *styleToggle =[[UISegmentedControl alloc] initWithItems:@[@"satellite", @"Streets", @"satellite Street"]];
    styleToggle.translatesAutoresizingMaskIntoConstraints = NO;
    styleToggle.selectedSegmentIndex = 2;
    [self.view insertSubview:styleToggle aboveSubview:self.mapView];
    [styleToggle addTarget:self action:@selector(changeStyle:) forControlEvents:UIControlEventValueChanged];
    
    // Configure autolayout constraints for the UISegmentedControl to align
    // at the bottom of the map view and above the Mapbox logo and attribution
    NSMutableArray *constraints = [NSMutableArray array];
    [constraints addObjectsFromArray:[NSLayoutConstraint constraintsWithVisualFormat:@"H:|-40-[styleToggle]-40-|" options:0 metrics:0 views:@{@"styleToggle":styleToggle}]];
    [constraints addObject:[NSLayoutConstraint constraintWithItem:styleToggle attribute:NSLayoutAttributeBottom relatedBy:NSLayoutRelationEqual toItem:self.mapView.logoView attribute:NSLayoutAttributeTop multiplier:1 constant:-20]];
    [self.view addConstraints:constraints];
     */
}

/*
- (void)changeStyle:(UISegmentedControl *)sender {
     NSString* filePath = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) objectAtIndex:0];
    switch(sender.selectedSegmentIndex){
        case 0:
        {
            NSString* fileName = @"Satellite.json";
            NSString* fileAtPath = [filePath stringByAppendingPathComponent:fileName];
            self.mapView.styleURL =[NSURL fileURLWithPath: fileAtPath];
        }
            break;
        case 1:
        {
            NSString* fileName = @"street.json";
            NSString* fileAtPath = [filePath stringByAppendingPathComponent:fileName];
            self.mapView.styleURL =[NSURL fileURLWithPath: fileAtPath];
        }
            break;
        case 2:
        {
            NSString* fileName = @"SatelliteStreet.json";
            NSString* fileAtPath = [filePath stringByAppendingPathComponent:fileName];
            self.mapView.styleURL =[NSURL fileURLWithPath: fileAtPath];
        }
            break;
    }
}
 */
- (void)mapView:(MGLMapView *)mapView didFinishLoadingStyle:(MGLStyle *)style {
    /*
    MGLRasterTileSource *source = [[MGLRasterTileSource alloc] initWithIdentifier:@"dg-imagry"
                                                                 tileURLTemplates:@[@"https://api.mapbox.com/v4/digitalglobe.nal0g75k/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNqZ2Qwcm8zYzJ3eGszM215ZTd3N2k4cmUifQ.Vs-RbB3JQxK2DXbqkBPt7w"]
                                                                          options:@{ MGLTileSourceOptionTileSize: @256}];
    MGLRasterStyleLayer *rasterLayer = [[MGLRasterStyleLayer alloc] initWithIdentifier:@"dg-imagrys" source:source];
    
    [mapView.style addSource:source];
  [mapView.style addLayer:rasterLayer];
    */
    for (MGLStyleLayer * layer in style.layers) {
        NSLog(@"%@",layer.identifier);
        if ([layer.identifier isEqualToString:@"qld-select"]) {
            self.pointStyleLayer = layer;
        }
        /*
        else if ([layer.identifier isEqualToString:@"qld-4"])
        {
            self.qld4StyleLayer=layer;
        }
         */
    }
    [mapView setCenterCoordinate:CLLocationCoordinate2DMake(-28.267,153.118)
                       zoomLevel:5
                        animated:YES];
    // Load a tileset containing U.S. states and their population density. For more information about working with tilesets, see: https://www.mapbox.com/help/studio-manual-tilesets/
    /*
    NSURL *url = [NSURL URLWithString:@"mapbox://examples.69ytlgls"];
    
    MGLVectorSource *source = [[MGLVectorSource alloc] initWithIdentifier:@"state-source" configurationURL:url];
    [style addSource:source];
    
    MGLFillStyleLayer *layer = [[MGLFillStyleLayer alloc] initWithIdentifier:@"state-layer" source:source];
    
    // Access the tileset layer.
    layer.sourceLayerIdentifier = @"stateData_2-dx853g";
    
    // Create a stops dictionary. This defines the relationship between population density and a UIColor.
    NSDictionary *stops = @{
                            @0: [MGLStyleValue valueWithRawValue:[UIColor yellowColor]],
                            @600: [MGLStyleValue valueWithRawValue:[UIColor redColor]],
                            @1200: [MGLStyleValue valueWithRawValue:[UIColor blueColor]]
                            };
    
    // Style the fill color using the stops dictionary, exponential interpolation mode, and the feature attribute name.
    layer.fillColor = [MGLStyleValue valueWithInterpolationMode:MGLInterpolationModeExponential
                                                    sourceStops:stops
                                                  attributeName:@"density"
                                                        options:@{MGLStyleFunctionOptionDefaultValue: [MGLStyleValue valueWithRawValue:[UIColor whiteColor]]}];
    
    // Insert the new layer below the Mapbox Streets layer that contains state border lines. See the layer reference for more information about layer names: https://www.mapbox.com/vector-tiles/mapbox-streets-v7/
    MGLStyleLayer *symbolLayer = [style layerWithIdentifier:@"admin-3-4-boundaries"];
    
    [style insertLayer:layer belowLayer:symbolLayer];
     */
    
}

- (void)handleTap:(UITapGestureRecognizer *)gesture {
    
    // Get the CGPoint where the user tapped.
    CGPoint spot = [gesture locationInView:self.mapView];
    
    // Access the features at that point within the state layer.
//    NSArray *features = [self.mapView visibleFeaturesAtPoint:spot
//                                inStyleLayersWithIdentifiers:[NSSet setWithObject:@"qld_scdbgeojson"]];
    NSArray *features = [self.mapView visibleFeaturesAtPoint:spot];
    id  feature =features.lastObject;
    if (feature && [feature isKindOfClass:[MGLPointFeature class]]) {
     //   [self showCallout:feature];
      //  MyCustomPointAnnotation *pointA = [[MyCustomPointAnnotation alloc]init];
      //  pointA.title =[[feature attributeForKey:@"objectid"] stringValue];
        NSString *  mb_id=[feature attributeForKey:@"mb_id"];
 
        NSString * jsonFilter=[NSString stringWithFormat:@"[\"all\",[\"match\",[\"get\",\"mb_id\"],[\"\",\"%@\"],true,false]]",mb_id];
        NSString * jsonString =[NSString stringWithFormat: @"[\"match\",[\"string\",[\"get\",\"mb_id\"]],\"%@\",\"marker-15\",\"bar-15\"]",mb_id];
        NSData *data = [jsonString dataUsingEncoding:NSUTF8StringEncoding];
        id json = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
            NSExpression * expression =[NSExpression expressionWithMGLJSONObject:json];

        self.pointStyleLayer.predicate=[NSPredicate predicateWithFormat:@"mb_id=%@",mb_id];
         

    }
    else
    {
        NSString * jsonString =[NSString stringWithFormat: @"[\"match\",[\"string\",[\"get\",\"mb_id\"]],\"-1\",\"marker-15\",\"bar-15\"]"];
        NSData *data = [jsonString dataUsingEncoding:NSUTF8StringEncoding];
        id json = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
        NSExpression * expression =[NSExpression expressionWithMGLJSONObject:json];
        
       // self.pointStyleLayer.iconImageName=expression;
        self.pointStyleLayer.predicate=[NSPredicate predicateWithFormat:@"mb_id=-1"];
    }
    

    
    // Get the name of the selected state.
  //  NSString *state = [feature attributeForKey:@"qld_scdbgeojson"];
    
  //  [self changeOpacityBasedOn:state];
}
- (void)showCallout:(MGLPointFeature *)feature {
    MGLPointFeature *point = [[MGLPointFeature alloc] init];
    point.title =[NSString stringWithFormat:@"%ld",[feature.attributes[@"objectid"] integerValue]];
    point.coordinate = feature.coordinate;
    
    // Selecting an feature that doesn’t already exist on the map will add a new annotation view.
    // We’ll need to use the map’s delegate methods to add an empty annotation view and remove it when we’re done selecting it.
    [self.mapView selectAnnotation:point animated:YES];
}
- (void)mapView:(MGLMapView *)mapView didSelectAnnotation:(id <MGLAnnotation>)annotation {
    self.anno =annotation;
}
- (BOOL)mapView:(MGLMapView *)mapView annotationCanShowCallout:(id <MGLAnnotation>)annotation {
    return YES;
}

- (void)mapView:(MGLMapView *)mapView didDeselectAnnotation:(id <MGLAnnotation>)annotation {
    [mapView removeAnnotation:annotation];
}

- (MGLAnnotationView *)mapView:(MGLMapView *)mapView viewForAnnotation:(id <MGLAnnotation>)annotation {
    // Create an empty view annotation. Set a frame to offset the callout.
    if ([annotation isKindOfClass:[MyCustomPointAnnotation class]]) {
        NSString *reuseIdentifier = @"reusableDotView";
        
        // For better performance, always try to reuse existing annotations.
        MGLAnnotationView *annotationView = [mapView dequeueReusableAnnotationViewWithIdentifier:reuseIdentifier];
        
        // If there’s no reusable annotation view available, initialize a new one.
        if (!annotationView) {
            annotationView = [[MGLAnnotationView alloc] initWithReuseIdentifier:reuseIdentifier];
            UIImage *image = [UIImage imageNamed:@"pin"];
            image = [image imageWithAlignmentRectInsets:UIEdgeInsetsMake(0, 0, image.size.height/2, 0)];
            UIImageView *imgView = [[UIImageView alloc] initWithImage:image];
            annotationView.frame = CGRectMake(0, 0, 19, 36);
           // annotationView.layer.cornerRadius = annotationView.frame.size.width / 2;
          //  annotationView.layer.borderColor = [UIColor whiteColor].CGColor;
          //  annotationView.layer.borderWidth = 4.0;
          //  annotationView.backgroundColor = [UIColor colorWithRed:0.03 green:0.80 blue:0.69 alpha:1.0];
            imgView.autoresizingMask=UIViewAutoresizingFlexibleWidth|UIViewAutoresizingFlexibleHeight|UIViewAutoresizingFlexibleTopMargin|UIViewAutoresizingFlexibleLeftMargin;
            [annotationView addSubview:imgView];
        }
        
        return annotationView;
    }
    else
    {
        return [[MGLAnnotationView alloc] initWithFrame:CGRectMake(0, 0, 20, 20)];
    }
    
}
- (MGLAnnotationImage *)mapView:(MGLMapView *)mapView imageForAnnotation:(id <MGLAnnotation>)annotation {
    
    if ([annotation isKindOfClass:[MyCustomPointAnnotation class]]) {
        MGLAnnotationImage *annotationImage = [mapView dequeueReusableAnnotationImageWithIdentifier:@"camera"];
        
        // If there is no reusable annotation image available, initialize a new one.
        if (!annotationImage) {
            UIImage *image = [UIImage imageNamed:@"pin"];
            image = [image imageWithAlignmentRectInsets:UIEdgeInsetsMake(0, 0, image.size.height/2, 0)];
            annotationImage = [MGLAnnotationImage annotationImageWithImage:image reuseIdentifier:@"pin"];
        }
        
        return annotationImage;
    }
    return nil;
}

- (UIView *)mapView:(MGLMapView *)mapView leftCalloutAccessoryViewForAnnotation:(id<MGLAnnotation>)annotation
{
  // Callout height is fixed; width expands to fit its content.
    
    UIButton * btn = [UIButton buttonWithType:(UIButtonTypeCustom)];
    [btn setTitle:@"nearest" forState:(UIControlStateNormal)];
    btn.frame=CGRectMake(0, 0, 80, 40);
    [btn setTitleColor:[UIColor blueColor] forState:UIControlStateNormal];
    btn.tag=1002;
    return btn;
}
-(void)findNearst
{
    [self.mapView deselectAnnotation:self.anno animated:NO];
   
    self.anno=nil;
}
- (UIView *)mapView:(MGLMapView *)mapView rightCalloutAccessoryViewForAnnotation:(id<MGLAnnotation>)annotation
{
    UIButton * btn= [UIButton buttonWithType:UIButtonTypeDetailDisclosure];
    btn.tag=1001;
    return btn;
}

- (void)mapView:(MGLMapView *)mapView annotation:(id<MGLAnnotation>)annotation calloutAccessoryControlTapped:(UIControl *)control
{
    // Hide the callout view.
    [self.mapView deselectAnnotation:annotation animated:NO];
    /*
    if (control.tag ==1001) {
        [self fetchDataByID:[annotation.title integerValue] result:^(NSDictionary * _Nonnull data) {
            DetailsViewController * deVC = [[DetailsViewController alloc] init];
            deVC.data =[data objectForKey:@"data"];
            [self.navigationController pushViewController:deVC animated:YES];
            
        }];
    }
    else
    {
        CGPoint p = [self ToWebMercatorLon:annotation.coordinate.longitude lat:annotation.coordinate.latitude];
        [self fetchNDataByX:p.x y:p.y result:^(NSDictionary * _Nonnull result) {
            NSArray * data = [result objectForKey:@"data"];
            for (NSDictionary * feature in data) {
                NSString * strGeom=[feature objectForKey:@"geom"];
                NSData *data = [strGeom dataUsingEncoding:NSUTF8StringEncoding];
                id geom = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
                NSArray * coor= [geom objectForKey:@"coordinates"];
                MyCustomPointAnnotation *pointA = [[MyCustomPointAnnotation alloc]init];
                pointA.title =[[feature objectForKey:@"objectid"] stringValue];
                pointA.coordinate =[self convertWebMercatorToGeographicX:[coor[0] doubleValue] Y:[coor[1] doubleValue] ];
                // pointA.willUseImage = YES;
                [self.mapView addAnnotation:pointA];
            }
        }];
    }
     */
}
- (CLLocationCoordinate2D)convertWebMercatorToGeographicX:(double)mercX Y:(double)mercY {
    // define earth
    const double earthRadius = 6378137.0;
    // handle out of range
    if (fabs(mercX) < 180 && fabs(mercY) < 90)
        return kCLLocationCoordinate2DInvalid;
    // this handles the north and south pole nearing infinite Mercator conditions
    if ((fabs(mercX) > 20037508.3427892) || (fabs(mercY) > 20037508.3427892)) {
        return kCLLocationCoordinate2DInvalid;
    }
    // math for conversion
    double num1 = (mercX / earthRadius) * 180.0 / M_PI;
    double num2 = floor(((num1 + 180.0) / 360.0));
    double num3 = num1 - (num2 * 360.0);
    double num4 = ((M_PI_2 - (2.0 * atan(exp((-1.0 * mercY) / earthRadius)))) * 180 / M_PI);
    // set the return
    CLLocationDegrees lattitude = num4;
    CLLocationDegrees longitude = num3;
    CLLocationCoordinate2D geoLocation = CLLocationCoordinate2DMake(lattitude, longitude);
    return geoLocation;
}
-(CGPoint)ToWebMercatorLon:(double) mercatorX_lon lat:(double) mercatorY_lat
{
    if (!(fabs(mercatorX_lon) > 180 || fabs(mercatorY_lat) > 90))
      {
          double num = mercatorX_lon * 0.017453292519943295;
          double x = 6378137.0 * num;
          double a = mercatorY_lat * 0.017453292519943295;
          double mercatorX_lon = x;
          double mercatorY_lat = 3189068.5 * log((1.0 + sin(a)) / (1.0 - sin(a)));
          return CGPointMake(mercatorX_lon, mercatorY_lat);
      }
     return CGPointMake(0, 0);
    
    
    
}
/*
- (void)mapView:(MGLMapView *)mapView didAddAnnotationViews:(NS_ARRAY_OF(MGLAnnotationView *) *)annotationViews
{
    for (MGLAnnotationView *annView in annotationViews)
    {
        CGRect endFrame = annView.frame;
        annView.frame=CGRectMake(endFrame.origin.x+8, endFrame.origin.y+5, 9, 18);
     //   annView.frame = CGRectOffset(endFrame, 0, -15);
        [UIView animateWithDuration:1.0 delay:0.0 usingSpringWithDamping:0.4 initialSpringVelocity:1.0 options:0 animations:^{
            
          annView.frame = endFrame;
            
        } completion:^(BOOL finished) {
        }];
    }
}
 */
- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}


@end
