const {defineConfig}=require('@playwright/test');
module.exports=defineConfig({testDir:'./tests',testMatch:'s10-multimodal.visual.spec.js',
workers:1,timeout:45000,reporter:'line',outputDir:'/tmp/s10-multimodal-playwright',
use:{baseURL:'http://127.0.0.1:4174',headless:true,acceptDownloads:true},
webServer:{command:'python3 -m http.server 4174 --bind 127.0.0.1',url:'http://127.0.0.1:4174',reuseExistingServer:!process.env.CI}});
