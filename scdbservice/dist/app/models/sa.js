'use strict';

class Sa {
    constructor(ogc_fid, geometry, objectid, x, y, z, name, zone, zone_easti, zone_north, h_datum, h_order, h_class, h_fixing, h_purpose, h_authorit, h_adjusted, h_position, h_localunc, h_entrydat, h_comment, v_datum, gs_sep, v_order, v_class, v_fixing, v_purpose, v_authorit, v_adjusted, v_position, v_localunc, v_entrydat, v_comment, marktype, specattrib, gone, wasnow, dupmarkno, no_50000, no_10000, no_2500, symbology) {
        this.ogc_fid = ogc_fid;
        this.geometry = geometry;
        this.objectid = objectid;
        this.x = x;
        this.y = y;
        this.z = z;
        this.name = name;
        this.zone = zone;
        this.zone_easti = '';
        this.zone_north = '';
        this.h_datum = h_datum;
        this.h_order = h_order;
        this.h_class = h_class;
        this.h_fixing = h_fixing;
        this.h_purpose = h_purpose;
        this.h_authorit = h_authorit;
        this.h_adjusted = h_adjusted;
        this.h_position = h_position;
        this.h_localunc = h_localunc;
        this.h_entrydat = h_entrydat;
        this.h_comment = h_comment;
        this.v_datum = v_datum;
        this.gs_sep = gs_sep;
        this.v_order = v_order;
        this.v_class = v_class;
        this.v_fixing = v_fixing;
        this.v_purpose = v_purpose;
        this.v_authorit = v_authorit;
        this.v_adjusted = v_adjusted;
        this.v_position = v_position;
        this.v_localunc = v_localunc;
        this.v_entrydat = v_entrydat;
        this.v_comment = v_comment;
        this.marktype = marktype;
        this.specattrib = specattrib;
        this.gone = gone;
        this.wasnow = wasnow;
        this.dupmarkno = dupmarkno;
        this.no_50000 = no_50000;
        this.no_10000 = no_10000;
        this.no_2500 = no_2500;
        this.symbology = symbology;

        this.v_data = "No";
        if (this.v_fixing) {
            this.v_data = "Yes";
        }
        this.h_data = "No";
        if (h_fixing) {
            this.h_data = "Yes";
        }
    }
}

module.exports = Sa;