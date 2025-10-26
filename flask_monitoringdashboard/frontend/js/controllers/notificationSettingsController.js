export function NotificationSettingsController($scope, $http, menuService, endpointService) {
    endpointService.reset();
    menuService.reset('notification_settings');

    $scope.notification_config = {};

    $http.get('api/deploy_notification_config').then(function (response) {
        $scope.notification_config = response.data;
    });

}
