from flask import jsonify

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure

from flask_monitoringdashboard.controllers.exceptions import get_exceptions_with_timestamp
from flask_monitoringdashboard.core.telemetry import post_to_back_if_telemetry_enabled
from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.database.exception_info import count_grouped_exceptions


@blueprint.route('/api/exception_info/<offset>/<per_page>')
@secure
def get_exception_info(offset, per_page):
    """
    Get information about all the exceptions that have occured for all endpoint
    :return: A JSON-list with a JSON-object per endpoint
    """
    post_to_back_if_telemetry_enabled(**{'name': 'exception_info'}) # Ved ikke 100% hvorfor, tror det er business behov, ikke et funktionelt behov som sådan
    with session_scope() as session:
        exceptions = get_exceptions_with_timestamp(session, offset, per_page)
        
        return jsonify(exceptions)
    
@blueprint.route('/api/num_exceptions')
@secure
def num_exceptions():
    post_to_back_if_telemetry_enabled(**{'name': f'num_exceptions'})
    with session_scope() as session:
        return jsonify(count_grouped_exceptions(session))
