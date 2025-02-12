// dette er frontend, husk "npm run dev" fra frontend/ for at kunne se dine ændringer
// Opsætning første gang: npm install --save-dev webpack webpack-cli babel-loader @babel/core @babel/preset-env

export function ExceptionController ($scope, $http, menuService, paginationService, endpointService) {
    endpointService.reset();
    // Hvis værdien 'new_dashboard' nedenfor ændres skal den også ændres i menuService, men den bruges ingen andre steder
    menuService.reset('new_dashboard'); // Fokus når man klikker på den i menuen (den bliver hvid og de andre bliver grå)

    // Route http://127.0.0.1:4200/dashboard/new_dashboard sættes i frontend/app.js

    $scope.table = []; // scope bruges i static/pages/new_dashboard.html
    // Hvis static/pages/new_dashboard.html filen skal renames, skal frontend/app.js lige opdateres

    /* 
        API og frontend virker til at køre på samme port så vidt jeg har forstået, og API routing specificeres i view layer

        filer der muliggør API lige nu (fra bunden og op):
            database/exception_info -> controllers/exceptions -> views/excpetion.py --api--> frontend/js/controllers/exceptionInfo.js
       
    */
    paginationService.init('exceptions');
    $http.get('api/num_exceptions').then(function (response) {
        paginationService.setTotal(response.data);
    });

    paginationService.onReload = function () {
        // formService.isLoading = true; ?
        $http.get('api/exception_info/' + paginationService.getLeft() + '/' + paginationService.perPage).then(function (response) {
            $scope.table = response.data;
            // formService.isLoading = false; ?
        });
    };
};