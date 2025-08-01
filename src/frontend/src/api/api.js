const endpoints = {
    health : "/health/", //GET
    login : "/login/", //GET
    grid :"/grid/", //POST
    addName:"/grid/add/", //POST
    removeName:"/grid/remove/", //DELETE
    allocateShift:"/grid/allocate", //POST
    hours:"/hours/", //GET
    upload:"/upload/", //POST
    download:"/download/", //POST
    resetAll:"/reset-all/", //DELETE
    compress:"/grid/compressed/", //POST
    swapNames:"/grid/swap-names/", //POST
}

export default endpoints;
