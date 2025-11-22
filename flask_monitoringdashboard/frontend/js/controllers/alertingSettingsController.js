export function AlertingSettingsController($scope, $http, menuService, endpointService) {
    endpointService.reset();
    menuService.reset('alerting_settings');

    $scope.alert_config = {};

    $http.get('api/deploy_alert_config').then(function (response) {
        $scope.alert_config = response.data;
    });

    $scope.labels = {
        'smtp_host': 'SMTP Host',
        'smtp_port': 'SMTP Port',
        'smtp_user': 'SMTP User',
        'smtp_to': 'SMTP To Address(es)',
        'chat_platform': 'Chat Platform',
        'repository_owner': 'Github Repository Owner',
        'repository_name': 'Github Repository Name'
    };

}
