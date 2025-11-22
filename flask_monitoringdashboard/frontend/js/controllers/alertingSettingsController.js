export function AlertingSettingsController($scope, $http, menuService, endpointService) {
    endpointService.reset();
    menuService.reset('alerting_settings');

    $scope.alert_config = {};

    $http.get('api/deploy_alert_config').then(function (response) {
        $scope.alert_config = response.data;
    });

    $scope.alertSections = {
        EMAIL: [
            {label: 'SMTP Host', key: 'smtp_host'},
            {label: 'SMTP Port', key: 'smtp_port'},
            {label: 'SMTP User', key: 'smtp_user'},
            {label: 'SMTP To Address(es)', key: 'smtp_to'}
        ],
        CHAT: [
            {label: 'Chat Platform', key: 'chat_platform'}
        ],
        GITHUB: [
            {label: 'Github Repository Owner', key: 'repo_owner'},
            {label: 'Github Repository Name', key: 'repo_name'}
        ]
    };

    $scope.isAlertingEnabled = function (type) {
        console.log($scope.alert_config.type);
        console.log(type);
        return $scope.alert_config.alert_enabled === true &&
            (type === null ||
                ($scope.alert_config.type &&
                    $scope.alert_config.type.includes(type)));
    };

}
