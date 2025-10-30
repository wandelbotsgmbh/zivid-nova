# Static Assets

This directory contains static assets served by the Zivid Nova API.

## Stoplight Elements

The UI for the OpenAPI documentation is powered by [Stoplight Elements](https://github.com/stoplightio/elements).

### Current Version
- **Version**: 9.0.8
- **Location**: `static/stoplight-9.0.8/`
- **Files**:
  - `web-components.min.js` - Web components bundle
  - `styles.min.css` - Styles bundle
  - `VERSION.txt` - Version metadata

### Versioning Strategy
Each version of Stoplight Elements is stored in its own directory with the version number in the path (e.g., `stoplight-9.0.8`). This approach:
- Makes it clear which version is deployed
- Allows multiple versions to coexist during migration
- Simplifies rollback if needed
- Enables cache busting when upgrading

### Updating Stoplight Elements

1. **Check for new version:**
   ```bash
   npm view @stoplight/elements version
   ```

2. **Download new version files:**
   ```bash
   VERSION="x.y.z"  # Replace with actual version
   mkdir -p static/stoplight-${VERSION}
   curl -L -o static/stoplight-${VERSION}/web-components.min.js \
     "https://unpkg.com/@stoplight/elements@${VERSION}/web-components.min.js"
   curl -L -o static/stoplight-${VERSION}/styles.min.css \
     "https://unpkg.com/@stoplight/elements@${VERSION}/styles.min.css"
   ```

3. **Create VERSION.txt:**
   ```bash
   cat > static/stoplight-${VERSION}/VERSION.txt << EOF
   Stoplight Elements Version: ${VERSION}
   Downloaded: $(date +%Y-%m-%d)
   Source: https://unpkg.com/@stoplight/elements@${VERSION}/
   NPM Package: @stoplight/elements
   EOF
   ```

4. **Update the application:**
   - Edit `zivid_nova/app.py`
   - Update the `STOPLIGHT_VERSION` constant to the new version
   - Test the application

5. **Clean up old version (optional):**
   ```bash
   rm -rf static/stoplight-<old-version>
   ```

## Other Assets
- `app_icon.png` - Application icon for homescreen
