const {defineConfig}=require('@playwright/test');
module.exports=defineConfig({
 testDir:'./tests',testMatch:/s09-(p0|implementation)\.visual\.spec\.js/,
 timeout:60000,workers:1,reporter:'line',
 outputDir:process.env.S09_QA_OUTPUT || '/tmp/bigdata-s09-playwright',
 use:{baseURL:'http://127.0.0.1:4173',headless:true,
  launchOptions:process.env.S09_CHROME ? {executablePath:process.env.S09_CHROME} : {}},
 webServer:{command:'python3 -m http.server 4173 --bind 127.0.0.1',url:'http://127.0.0.1:4173',reuseExistingServer:!process.env.CI}
});
