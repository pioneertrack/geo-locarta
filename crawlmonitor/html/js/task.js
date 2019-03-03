$(document).ready( function() {

                //Second example that shows all options.
                var waTable = $('#taskList').WATable({
                //data: generateSampleData(100), //Initiate with data if you already have it
                debug:false,                //Prints some debug info to console
                dataBind: true,             //Auto-updates table when changing data row values. See example below. (Note. You need a column with the 'unique' property)
                pageSize: 10,                //Initial pagesize
                pageSizePadding: false,      //Pads with empty rows when pagesize is not met
                //transition: 'slide',       //Type of transition when paging (bounce, fade, flip, rotate, scroll, slide).Requires https://github.com/daneden/animate.css.
                //transitionDuration: 0.2,    //Duration of transition in seconds.
                filter: false,               //Show filter fields
                sorting: false,              //Enable sorting
                sortEmptyLast:false,         //Empty values will be shown last
                columnPicker: false,         //Show the columnPicker button
                pageSizes: [],  //Set custom pageSizes. Leave empty array to hide button.
                hidePagerOnEmpty: true,     //Removes the pager if data is empty.
                checkboxes: false,           //Make rows checkable. (Note. You need a column with the 'unique' property)
                checkAllToggle:false,        //Show the check-all toggle
                preFill: false,              //Initially fills the table with empty rows (as many as the pagesize).
                //url: '/someWebservice'    //Url to a webservice if not setting data manually as we do in this example
                //urlData: { report:1 }     //Any data you need to pass to the webservice
                //urlPost: true             //Use POST httpmethod to webservice. Default is GET.
                types: {                    //If you want, you can supply some properties that will be applied for specific data types.
                    string: {
                        //filterTooltip: "Giggedi..."    //What to say in tooltip when hoovering filter fields. Set false to remove.
                        //placeHolder: "Type here..."    //What to say in placeholder filter fields. Set false for empty.
                    },
                    number: {
                        decimals: 1   //Sets decimal precision for float types
                    },
                    bool: {
                        //filterTooltip: false
                    },
                    date: {
                      utc: true,            //Show time as universal time, ie without timezones.
                      //format: 'yy/dd/MM',   //The format. See all possible formats here http://arshaw.com/xdate/#Formatting.
                      datePicker: true      //Requires "Datepicker for Bootstrap" plugin (http://www.eyecon.ro/bootstrap-datepicker).
                    }
                },
                actions: null,
                tableCreated: function(data) {    //Fires when the table is created / recreated. Use it if you want to manipulate the table in any way.
                    console.log('table created'); //data.table holds the html table element.
                    //console.log(data);            //'this' keyword also holds the html table element.
                },
                rowClicked: function(data) {      //Fires when a row or anything within is clicked (Note. You need a column with the 'unique' property).
                    console.log('row clicked');   //data.event holds the original jQuery event.
                                                  //data.row holds the underlying row you supplied.
                                                  //data.index holds the index of row in rows array (Useful when you want to remove the row)
                                                  //data.column holds the underlying column you supplied.
                                                  //data.checked is true if row is checked. (Set to false/true to have it unchecked/checked)
                                                  //'this' keyword holds the clicked element.
                    
                    
                }
     
            }).data('WATable');  //This step reaches into the html data property to get the actual WATable object. Important if you want a reference to it as we want here.
            //Generate some data
            var token =Cookies.get('token');
            
            if(token)
            {
                url = "api/task/"
                $.ajax({
                    url: url,
                    headers: {"Authorization": "JWT "+token}

                }).then(function(data) {
                 // console.log(data);
                  var rows = generateRowData(data);
                  waTable.setData(rows);  //Sets the data.
                  Platform.performMicrotaskCheckpoint();
                }).catch(function(error){
                    window.location.href = "./login.html";
                    //alert(error);
                });
    
            }
            else
            {
               // window.location.href = "./login.html";
            }
            
           

        });
        //Generates some data.
        function generateRowData(data) {
            //First define the columns
            var cols = {
                taskId: {
                    index: 1, //The order this column should appear in the table
                    type: "number", //The type. Possible are string, number, bool, date(in milliseconds).
                    format: "<a href='./taskItem.html?taskid={0}' target='_blank'>{0}</a>",  //Used to format the data anything you want. Use {0} as placeholder for the actual data.
                    unique: false,  //This is required if you want checkable rows, databinding or to use the rowClicked callback. Be certain the values are really unique or weird things will happen.
                    sortOrder: "desc", //Data will initially be sorted by this column. Possible are "asc" or "desc"
                    tooltip: "Task ID"

                },
                name: {
                    index: 2,
                    type: "string",
                    friendly: "Name",
                    cls: "", //apply some css classes
                    tooltip: "name", //Show some additional info about column
                    placeHolder: "" //Overrides default placeholder and placeholder specified in data types(row 34).
                },
                status: {
                    index: 3,
                    type: "string",
                    friendly: "status",
                    sorting: false, //dont allow sorting
                    tooltip: "status", //Show some additional info about column
                    filter: false //Removes filter field for this column
                },
                startTime: {
                    index: 4,
                    type: "date",
                    friendly: "startTime",
                    format: "",
                    tooltip: "startTime", //Show some additional info about column
                    filterTooltip: false //Turn off tooltip for this column
                }
            };
            /*
              Create the rows (This step is of course normally done by your web server). 
              What's worth mentioning is the special row properties. See some examples below.
              <column>Format allows you to override column format and have it formatted the way you want.
              <column>Cls allows you to add css classes on the cell(td) element.
              row-checkable allows you to prevent rows from being checkable.
              row-checked allows you to pre-check a row.
              row-cls allows you to add css classes to the row(tr) element.
            */
            var rows = [];
            
            for(var i=0;i< data.length;i++)
            {
                obj=data[i];
                //We leave some fields intentionally undefined, so you can see how sorting/filtering works with these.
                var row = {};
                row.taskId           = obj.id;
                row.name             = obj.name; 
                row.status              =obj.status; 
                row.startTime           = Date.UTC(obj.startTime);
                rows.push(row);
                
            }
            //Create the returning object. Besides cols and rows, you can also pass any other object you would need later on.
            var rowdata = {
                cols: cols,
                rows: rows,
                otherStuff: {
                    thatIMight: 1,
                    needLater: true
                }
            };
            return rowdata;
        }
       