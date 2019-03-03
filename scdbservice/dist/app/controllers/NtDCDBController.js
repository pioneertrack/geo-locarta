'use strict';
/* Load Task Data Access Object */

const NtDCDBDao = require('../dao/NtDCDBDao');

/* Load Controller Common function */
const ControllerCommon = require('./common/controllerCommon');

class NtDCDBController {

    constructor() {
        this.ntDCDBDao = new NtDCDBDao();
        this.common = new ControllerCommon();
    }
    findById(req, res) {
        let id = req.params.id;
        this.ntDCDBDao.findById(id).then(this.common.findSuccess(res)).catch(this.common.findError(res));
    }
    query(req, res) {
        let parcel = req.query.parcel;
        let survey_plan_number = req.query.survey_plan_number;

        this.ntDCDBDao.findByLegal(parcel, survey_plan_number).then(this.common.findSuccess(res)).catch(this.common.findError(res));
    }
}
module.exports = NtDCDBController;