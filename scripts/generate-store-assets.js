const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUTPUT_DIR = path.join(__dirname, '..', 'store-assets');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function generateScreenshots() {
    const browser = await chromium.launch({ headless: true });
    
    // Mobile viewport for app screenshots (1080x1920)
    const mobileContext = await browser.newContext({
        viewport: { width: 1080, height: 1920 },
        deviceScaleFactor: 1,
    });
    
    const mobilePage = await mobileContext.newPage();
    
    // Load the app
    const indexPath = path.join(__dirname, '..', 'index.html');
    await mobilePage.goto(`file://${indexPath}`);
    
    // Wait for initial content to load
    await mobilePage.waitForTimeout(2000);
    
    console.log('📸 Generating Screenshot 1: Home Grid...');
    // Screenshot 1: Home page with wallpaper grid
    await mobilePage.screenshot({
        path: path.join(OUTPUT_DIR, 'screenshot-1-home-grid.png'),
        fullPage: false,
    });
    
    console.log('📸 Generating Screenshot 2: S-Class Curated...');
    // Screenshot 2: Click S-CLASS CURATED button and show curated collection
    await mobilePage.click('button:has-text("S-CLASS CURATED")');
    await mobilePage.waitForTimeout(2000);
    await mobilePage.screenshot({
        path: path.join(OUTPUT_DIR, 'screenshot-2-s-class-curated.png'),
        fullPage: false,
    });
    
    console.log('📸 Generating Screenshot 3: Search...');
    // Screenshot 3: Search functionality
    await mobilePage.fill('#searchInput', 'Nature');
    await mobilePage.press('#searchInput', 'Enter');
    await mobilePage.waitForTimeout(2000);
    await mobilePage.screenshot({
        path: path.join(OUTPUT_DIR, 'screenshot-3-search.png'),
        fullPage: false,
    });
    
    console.log('📸 Generating Screenshot 4: Selection Mode...');
    // Screenshot 4: Selection mode (click some cards)
    await mobilePage.click('.card:nth-child(1)');
    await mobilePage.click('.card:nth-child(2)');
    await mobilePage.click('.card:nth-child(3)');
    await mobilePage.waitForTimeout(500);
    await mobilePage.screenshot({
        path: path.join(OUTPUT_DIR, 'screenshot-4-selection.png'),
        fullPage: false,
    });
    
    await mobileContext.close();
    
    // Generate Feature Graphic (1024x500)
    console.log('🎨 Generating Feature Graphic...');
    const featureContext = await browser.newContext({
        viewport: { width: 1024, height: 500 },
        deviceScaleFactor: 1,
    });
    
    const featurePage = await featureContext.newPage();
    const featureHtmlPath = path.join(__dirname, '..', 'store-assets', 'feature-graphic.html');
    await featurePage.goto(`file://${featureHtmlPath}`);
    await featurePage.waitForTimeout(1000);
    await featurePage.screenshot({
        path: path.join(OUTPUT_DIR, 'feature-graphic.png'),
        fullPage: false,
    });
    
    await featureContext.close();
    await browser.close();
    
    console.log('✅ All screenshots generated!');
}

generateScreenshots().catch(console.error);
