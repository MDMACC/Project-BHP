# Google Maps Embed Setup Instructions

## Getting the Correct Embed URL for 8033 Remmet Ave, Canoga Park, CA 91304

### Step 1: Get the Embed Code from Google Maps

1. **Go to Google Maps:** https://www.google.com/maps
2. **Search for your address:** `8033 Remmet Ave, Canoga Park, CA 91304`
3. **Click the "Share" button** (usually located in the left panel)
4. **Select "Embed a map"** tab
5. **Choose your preferred size:** 
   - Small: 400x300
   - Medium: 600x450 (recommended)
   - Large: 800x600
6. **Copy the iframe HTML code** provided

### Step 2: Extract the src URL

From the copied iframe code, extract only the `src` URL. It will look like:
```
https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d[coordinates]!2s8033%20Remmet%20Ave%2C%20Canoga%20Park%2C%20CA%2091304%2C%20USA!5e0!3m2!1sen!2sus!4v[timestamp]!5m2!1sen!2sus
```

### Step 3: Update the Website

1. **Open file:** `flask-app/templates/customer/home.html`
2. **Find line ~479** with the iframe src
3. **Replace the placeholder URL** with your actual Google Maps embed URL

### Current Location in Code

Look for this section around line 479:
```html
<iframe 
    src="REPLACE_THIS_URL_WITH_ACTUAL_GOOGLE_MAPS_EMBED_URL"
    width="100%" 
    height="100%" 
    style="border:0;" 
    allowfullscreen="" 
    loading="lazy" 
    referrerpolicy="no-referrer-when-downgrade"
    class="rounded-lg"
    onload="this.style.display='block';">
</iframe>
```

### Features Already Implemented

✅ **Interactive Map Widget** - Real embedded Google Maps  
✅ **Loading Animation** - Spinner while map loads  
✅ **Responsive Design** - Scales properly on all devices  
✅ **Professional Styling** - Rounded corners and shadow  
✅ **Fallback Link** - "Open in Google Maps" button below map  

### Troubleshooting

- **Map not loading?** Check if the embed URL is correct
- **Address not found?** Verify the address exists on Google Maps
- **Blank iframe?** Ensure you copied the complete embed URL

Once you update the src URL with the real Google Maps embed code, your website will display an actual interactive map widget showing your shop's exact location!
