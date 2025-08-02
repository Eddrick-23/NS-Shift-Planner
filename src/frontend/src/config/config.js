// import path from 'path';
// import fs from 'fs'
// import dotenv from 'dotenv';

// const envFile = path.resolve(process.cwd(), '.env.local')

// if (fs.existsSync((envFile))) {
//     dotenv.config({path:envFile})
// }

// function tryGetEnv(key,type) {
//     let variable = ""
//     if (type === "str") {
//         variable = process.env[key];
//     } 
//     if (type === "int") {
//         variable = parseInt(process.env[key]);
//     }
//     if (variable === "") {
//         throw new Error(`Environment variable ${key} is required but was not found.`);
//     }
//     return variable
// }
// const config = {
//     VITE_FRONTEND_PORT: tryGetEnv("VITE_FRONTEND_PORT", "int"),
//     VITE_VERSION: tryGetEnv("VITE_VERSION", "str"),
//     VITE_BACKEND_DOMAIN : tryGetEnv("VITE_BACKEND_DOMAIN","str"),
//     VITE_BASE_URL : tryGetEnv("VITE_BASE_URL","str"),
// }

// export default config
