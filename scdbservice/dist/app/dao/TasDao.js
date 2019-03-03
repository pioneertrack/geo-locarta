
'use strict';
/* Load Task entity */

const Tas = require('../models/tas');

/* Load DAO Common functions */
const daoCommon = require('./commons/daoCommon');

/**
 * Task Data Access Object
 */
class TasDao {

    constructor() {
        this.common = new daoCommon();
    }

    findById(id) {
        let sqlRequest = 'SELECT * ,ST_AsGeoJSON(wkb_geometry) as geom FROM tas20180310062806 WHERE ogc_fid=${id}';
        let sqlParams = { id: id };
        return this.common.find(sqlRequest, sqlParams).then(rows => {
            let tass = [];
            for (const row of rows) {
                tass.push(new Tas(row.ogc_fid, row.geom, row.objectid, row.pack_id, row.site_pk_id, row.order_symb, row.scs_name, row.zone, row.easting, row.northing, row.hor_datum, row.hor_class, row.hor_order, row.target_str, row.height, row.hgt_datum, row.hgt_class, row.hgt_order, row.markstatus, row.descript, row.ist_guid));
            }
            return tass;
        });
    }
    /**
     * Finds all entities.
     * @return all entities
     */
    findAll() {
        let sqlRequest = 'SELECT  *,ST_AsGeoJSON(wkb_geometry) as geom FROM tas20180310062806 order by ogc_fid desc fetch first 10 rows only';
        return this.common.findAll(sqlRequest).then(rows => {
            let tass = [];
            for (const row of rows) {
                tass.push(new Tas(row.ogc_fid, row.geom, row.objectid, row.pack_id, row.site_pk_id, row.order_symb, row.scs_name, row.zone, row.easting, row.northing, row.hor_datum, row.hor_class, row.hor_order, row.target_str, row.height, row.hgt_datum, row.hgt_class, row.hgt_order, row.markstatus, row.descript, row.ist_guid));
            }
            return tass;
        });
    }
    findByPaging(pageNum, pageCount) {
        let countSql = 'SELECT COUNT(*) AS count FROM tas20180310062806';
        let pagingSql = 'SELECT  *,ST_AsGeoJSON(wkb_geometry) as geom   FROM tas20180310062806  LIMIT ${limit} OFFSET ${offset} ';
        let sqlParams = { limit: pageCount, offset: pageNum * pageCount };
        return this.common.paging(countSql, pagingSql, sqlParams).then(data => {

            let tass = [];
            for (const row of data.rows) {
                tass.push(new Tas(row.ogc_fid, row.geom, row.objectid, row.pack_id, row.site_pk_id, row.order_symb, row.scs_name, row.zone, row.easting, row.northing, row.hor_datum, row.hor_class, row.hor_order, row.target_str, row.height, row.hgt_datum, row.hgt_class, row.hgt_order, row.markstatus, row.descript, row.ist_guid));
            }
            return { count: data.row.count, features: tass };
        });
    }
    findByNearst(x, y, n) {
        let point = 'SRID=4326;POINT(' + x + ' ' + y + ')';

        let sqlRequest = " SELECT *,ST_AsGeoJSON(wkb_geometry) as geom ,st_distance(wkb_geometry, ST_Transform(ST_GeomFromText($1),3857)) as d  \
             FROM tas20180310062806    \
             ORDER BY wkb_geometry <->ST_Transform(ST_GeomFromText($1),3857) limit $2";

        let sqlParams = [point, n];
        return this.common.find(sqlRequest, sqlParams).then(rows => {
            let tass = [];
            for (const row of rows) {
                tass.push({ distance: row.d, feature: new Tas(row.ogc_fid, row.geom, row.objectid, row.pack_id, row.site_pk_id, row.order_symb, row.scs_name, row.zone, row.easting, row.northing, row.hor_datum, row.hor_class, row.hor_order, row.target_str, row.height, row.hgt_datum, row.hgt_class, row.hgt_order, row.markstatus, row.descript, row.ist_guid) });
            }
            return tass;
        });
    }

}

module.exports = TasDao;