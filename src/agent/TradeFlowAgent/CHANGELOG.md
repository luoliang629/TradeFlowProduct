# Changelog

All notable changes to TradeFlowAgent will be documented in this file.

## [v2.1.0] - 2025-01-31

### 🚨 BREAKING CHANGES
- **Search API**: System now exclusively uses Jina Search API, no fallback to DuckDuckGo
- **Configuration requirement**: `JINA_API_KEY` is now mandatory for search functionality

### ✨ Added
- **Enhanced error handling**: Four distinct error types for better debugging:
  - `ConfigurationError`: Missing API configuration
  - `APIError`: API authentication, rate limiting, server errors
  - `NetworkError`: Connection issues, timeouts
  - `ParseError`: Response parsing failures
- **Automatic retry mechanism**: Exponential backoff retry for network errors (up to 3 attempts)
- **Quality metrics**: Enhanced search quality evaluation with multiple dimensions
- **Detailed error messages**: Clear instructions for resolving each error type

### 🗑️ Removed
- DuckDuckGo search implementation (`_duckduckgo_search` function)
- Search engine fallback mechanism
- Optional status of Jina API configuration

### 🔧 Changed
- **Search behavior**: Direct error throwing instead of fallback attempts
- **Configuration**: `JINA_API_KEY` changed from optional to required
- **Error strategy**: From "Jina → DuckDuckGo → Error" to "Jina → Error with clear instructions"
- **Documentation**: Updated to reflect Jina-only search implementation

### 📚 Documentation
- Updated `README.md` to mark Jina API as required
- Updated `.env.example` with clearer Jina API instructions
- Completely rewrote `docs/search_configuration.md` for Jina-only setup
- Updated search agent instructions to reflect no-fallback policy

## [v2.0.0] - 2025-01-26

### 🚨 BREAKING CHANGES
- **Removed Mock functionality**: All Mock data and simulation code have been completely removed
- **Real API only**: System now exclusively uses real APIs (Jina, Tendata, etc.)
- **Configuration changes**: `USE_MOCK_DATA` environment variable is no longer supported

### ✨ Added
- **Real-time enterprise information**: `company_info.py` now uses web search + content analysis for global company data
- **Enhanced error handling**: Clear, actionable error messages when APIs fail
- **End-to-end testing**: `test_e2e_no_mock.py` validates no Mock code remains
- **Global compatibility**: Enterprise search supports companies worldwide

### 🗑️ Removed
- `_mock_search()` function from `web_search.py` (286-428 lines of Mock data)
- `_mock_reader()` function from `jina_reader.py` (302-442 lines of Mock content)
- Mock data generation logic from `customs_query.py` (53-120 lines)
- `_generate_mock_companies()` function from `company_info.py`
- Mock fallback data from `b2b_search.py` (644-678 lines)
- `USE_MOCK_DATA` configuration from `config.py`
- All Mock-related documentation and examples

### 🔧 Changed
- **Degradation strategy**: Changed from "Jina → DuckDuckGo → Mock" to "Jina → DuckDuckGo → Clear error message"
- **Default behavior**: System now requires real API configuration for production use
- **Error responses**: API failures return structured error messages instead of fake data
- **Documentation**: Updated README.md and CLAUDE.md to reflect real API requirements

### 🚀 Performance
- **Reduced code complexity**: Removed over 500 lines of Mock code
- **Faster execution**: Eliminated Mock data checks and generation overhead
- **Cleaner architecture**: Simplified tool logic with single real API path

### 📚 Documentation
- Updated development principles to prioritize real APIs
- Added comprehensive API configuration guide
- Clarified production deployment requirements
- Removed all Mock-related setup instructions

### 🧪 Testing
- Created comprehensive end-to-end tests for Mock-free validation
- Updated unit tests to work with real APIs
- Added code analysis tests to prevent Mock code regression

### 🔐 Security
- Enhanced API key management guidance
- Removed development-time security risks from Mock data
- Improved error message security (no sensitive data exposure)

## Migration Guide

### For Developers
1. Remove `USE_MOCK_DATA=true` from your `.env` file
2. Configure real API keys:
   - `JINA_API_KEY` for enhanced search (optional)
   - `TENDATA_API_KEY` for customs data (required for customs queries)
3. Update any code that relied on Mock data behavior
4. Test with real APIs to ensure functionality

### For Users
- System now requires proper API configuration for full functionality
- Expect real data or clear error messages (no more simulated results)
- Better accuracy and reliability with real-time information

---

**Note**: This is a major version update that fundamentally changes how the system operates. The removal of Mock functionality ensures data integrity and prepares the system for production deployment.