const {defineConfig}=require('@playwright/test');
module.exports=defineConfig({
testDir:'./tests',testMatch:['s11-etl.visual.spec.js'],workers:1,timeout:45000,
reporter:'line',outputDir:'/tmp/s11-etl-playwright',
use:{baseURL:'http://127.0.0.1:4176',headless:true,acceptDownloads:true},
webServer:{command:'python3 -m http.server 4176 --bind 127.0.0.1',
url:'http://127.0.0.1:4176',reuseExistingServer:!process.env.CI}});
