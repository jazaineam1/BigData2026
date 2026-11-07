const {defineConfig}=require('@playwright/test');
module.exports=defineConfig({testDir:'./tests',testMatch:['tc2-guide.visual.spec.js'],workers:1,timeout:45000,reporter:'line',outputDir:'/tmp/tc2-playwright',use:{baseURL:'http://127.0.0.1:4175',headless:true},webServer:{command:'python3 -m http.server 4175 --bind 127.0.0.1',url:'http://127.0.0.1:4175',reuseExistingServer:!process.env.CI}});
