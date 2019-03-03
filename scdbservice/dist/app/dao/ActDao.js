'use strict';
/* Load Task entity */

const Act = require('../models/act');

/* Load DAO Common functions */
const daoCommon = require('./commons/daoCommon');

/**
 * Task Data Access Object
 */
class ActDao {

    constructor() {
        this.common = new daoCommon();
    }

    findById(id) {
        let sqlRequest = 'SELECT * ,ST_AsGeoJSON(wkb_geometry) as geom FROM act20180310062806 WHERE ogc_fid=${id}';
        let sqlParams = { id: id };
        return this.common.find(sqlRequest, sqlParams).then(rows => {
            let acts = [];
            for (const row of rows) {
                acts.push(new Act(row.ogc_fid, row.geom, row.objectid, row.type, row.name, row.construction, row.condition, row.lifecycle_stage, row.datum, row.easting, row.northing, row.hz_class, row.hz_order, row.rl_datum, row.reduced_level, row.ht_class, row.ht_order, row.mar_id, row.id, row.remarks, row.plans, row.hz_palm_order, row.ht_palm_order, row.district_name, row.division_name));
            }
            return acts;
        });
    }
    /**
     * Finds all entities.
     * @return all entities
     */
    findAll() {
        let sqlRequest = 'SELECT  *,ST_AsGeoJSON(wkb_geometry) as geom FROM act20180310062806 order by ogc_fid desc fetch first 10 rows only';
        return this.common.findAll(sqlRequest).then(rows => {
            let acts = [];
            for (const row of rows) {
                acts.push(new Act(row.ogc_fid, row.geom, row.objectid, row.type, row.name, row.construction, row.condition, row.lifecycle_stage, row.datum, row.easting, row.northing, row.hz_class, row.hz_order, row.rl_datum, row.reduced_level, row.ht_class, row.ht_order, row.mar_id, row.id, row.remarks, row.plans, row.hz_palm_order, row.ht_palm_order, row.district_name, row.division_name));
            }
            return acts;
        });
    }
    findByPaging(pageNum, pageCount) {
        let countSql = 'SELECT COUNT(*) AS count FROM act20180310062806';
        let pagingSql = 'SELECT  *,ST_AsGeoJSON(wkb_geometry) as geom   FROM act20180310062806  LIMIT ${limit} OFFSET ${offset} ';
        let sqlParams = { limit: pageCount, offset: pageNum * pageCount };
        return this.common.paging(countSql, pagingSql, sqlParams).then(data => {

            let acts = [];
            for (const row of data.rows) {
                acts.push(new Act(row.ogc_fid, row.geom, row.objectid, row.type, row.name, row.construction, row.condition, row.lifecycle_stage, row.datum, row.easting, row.northing, row.hz_class, row.hz_order, row.rl_datum, row.reduced_level, row.ht_class, row.ht_order, row.mar_id, row.id, row.remarks, row.plans, row.hz_palm_order, row.ht_palm_order, row.district_name, row.division_name));
            }
            return { count: data.row.count, features: acts };
        });
    }
    findByNearst(x, y, n) {
        let point = 'SRID=4326;POINT(' + x + ' ' + y + ')';

        let sqlRequest = " SELECT *,ST_AsGeoJSON(wkb_geometry) as geom ,st_distance(wkb_geometry, ST_Transform(ST_GeomFromText($1),3857)) as d  \
             FROM act20180310062806    \
             ORDER BY wkb_geometry <->ST_Transform(ST_GeomFromText($1),3857) limit $2";

        let sqlParams = [point, n];

        return this.common.find(sqlRequest, sqlParams).then(rows => {
            let acts = [];
            for (const row of rows) {
                acts.push({ distance: row.d, feature: new Act(row.ogc_fid, row.geom, row.objectid, row.type, row.name, row.construction, row.condition, row.lifecycle_stage, row.datum, row.easting, row.northing, row.hz_class, row.hz_order, row.rl_datum, row.reduced_level, row.ht_class, row.ht_order, row.mar_id, row.id, row.remarks, row.plans, row.hz_palm_order, row.ht_palm_order, row.district_name, row.division_name) });
            }
            return acts;
        });
    }

}

module.exports = ActDao;