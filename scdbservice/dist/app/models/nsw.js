'use strict';

class Nsw {
    constructor(ogc_fid, geometry, objectid, marktype, marknumber, markstatus, monumenttype, markalias, trigname, trigtype, monumentlocation, mgaeasting, mganorthing, mgazone, gdadate, gdaclass, gdaorder, ahdheight, ahddate, ahdclass, ahdorder, marksymbol, msoid, ausgeoid09, mgacsf, mgacon) {
        this.ogc_fid = ogc_fid;
        this.geometry = geometry;
        this.objectid = objectid;
        this.marktype = marktype;
        this.marknumber = marknumber;
        this.monumenttype = monumenttype;
        this.markalias = markalias;
        this.trigname = trigname;
        this.trigtype = trigtype;
        this.monumentlocation = monumentlocation;
        this.mgaeasting = mgaeasting;
        this.mganorthing = mganorthing;
        this.mgazone = mgazone;
        this.gdadate = gdadate;
        this.gdaclass = gdaclass;
        this.gdaorder = gdaorder;
  
        this.ahddate = ahddate;
        this.ahdclass = ahdclass;
        this.ahdorder = ahdorder;
        this.marksymbol = marksymbol;
        this.msoid = msoid;
        this.ausgeoid09 = ausgeoid09;
        this.mgacsf = mgacsf;
        this.mgacon = mgacon;
        if(ahdheight){
            this.ahdheight=ahdheight;
        }
        else{
            this.ahdheight='';
        }
        if (markstatus) {
            if (markstatus == "D") {
                this.markstatus = "FOUND";
            } else if (markstatus == "N") {
                this.markstatus = "NOT FOUND";
            } else if (markstatus == "U") {
                this.markstatus = "UNCERTAIN";
            } else if (markstatus == "R") {
                this.markstatus = "RESTRICTED";
            } else if (markstatus == "S") {
                this.markstatus = "SUBSIDENCE";
            }
        } else {
            this.markstatus = "N/A";
        }
        if (marksymbol) {
            let lastWord = marksymbol.substr(-1);
            if (lastWord == "R") {
                this.v_data = 'Yes';
                this.h_data = "Yes";
            } else if (lastWord == "P") {
                this.v_data = 'No';
                this.h_data = "Yes";
            } else if (lastWord == "G") {
                this.v_data = "Yes";
                this.h_data = "No";
            } else if (lastWord == "B") {
                this.v_data = "Appr.";
                this.h_data = "Appr.";
            }
        }
    }
}

module.exports = Nsw;