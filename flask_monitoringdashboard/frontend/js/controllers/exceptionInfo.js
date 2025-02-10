// dette er frontend, husk "npm run build" fra frontend/ for at kunne se dine ændringer
// Opsætning første gang: npm install --save-dev webpack webpack-cli babel-loader @babel/core @babel/preset-env

export function ExceptionController ($scope, $http, menuService, endpointService) {
    endpointService.reset();
    // Hvis værdien 'new_dashboard' nedenfor ændres skal den også ændres i menuService, men den bruges ingen andre steder
    menuService.reset('new_dashboard'); // Fokus når man klikker på den i menuen (den bliver hvid og de andre bliver grå)

    // Route http://127.0.0.1:4200/dashboard/new_dashboard sættes i frontend/app.js

    $scope.message = "Welcome to the New Dashboard!"; // scope bruges i static/pages/new_dashboard.html
    $scope.table = [];
    // Hvis static/pages/new_dashboard.html filen skal renames, skal frontend/app.js lige opdateres

    /* 
        API og frontend virker til at køre på samme port så vidt jeg har forstået, og API routing specificeres i view layer

        filer der muliggør API lige nu (fra bunden og op):
            database/exception_info -> controllers/exceptions -> views/excpetion.py --api--> frontend/js/controllers/exceptionInfo.js
       
    */
    $http.get('api/exception_info').then(function (response) {
        console.log("DATA START");
        console.log(response.data);
        console.log("DATA SLUT");
        $scope.table = response.data;
    });

};