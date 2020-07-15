from _algae.strings import prefix, suffix

from .locator import Locator
from .query import By
from .response import Miss

__all__ = ['Locators']

class _LocationRef(type):
    def __contains__(cls, key: str):
        return hasattr(cls, key)

    def __getitem__(cls, key: str):
        if isinstance(key, str) and hasattr(cls, key):
            return getattr(cls, key)
        else:
            return Miss

    def __iter__(cls):
        for locator in [l for l in dir(cls) if not l.startswith('_')]:
            yield locator

    def count(cls): return len([l for l in dir(cls) if not l.startswith('_')])

class Locators(metaclass=_LocationRef):
    TopNavigation = Locator('top-nav', By.ID)
    EarthTimeLogo = Locator('menu-logo', By.ID)
    StoriesMenu = Locator('stories-menu-choice', By.ID)
    DataLibraryMenu = Locator('layers-menu-choice', By.ID)
    ShareButton = Locator('share-menu-choice', By.ID)
    StoryEditorButton = Locator('story-editor-menu-choice', By.ID)

    LocationSearchContainer = Locator('div.location_search_div', By.ID)
    LocationSearchIcon = Locator('location_search_icon', By.ID)
    LocationSearchInput = Locator('location_search', By.ID)
    LocationSearchClearButton = Locator('location_search_clear_icon', By.ID)

    StoriesMenuContainer = Locator('theme-menu', By.ID)
    StoriesMenuHeader = Locator("#theme-menu > label[for='theme-selection']")
    ThemeMenu = Locator('div.themes-div')
    ThemeHeaders = Locator("div.themes-div > h3[data-enabled='true']", list_=True)
    ThemeTables = Locator("div.themes-div > table[data-enabled='true']", list_=True)
    ThemeHeader = Locator([
        lambda id: "h3#%s" % id, 
        lambda ac: "div.themes-div > h3[aria-controls='%s']" % prefix(ac, 'theme_')
    ])
    ThemeTable = Locator([
        lambda id: "table#%s" % prefix(id, 'theme_'),
        lambda alb: "div.themes-div > table[aria-labelledby='%s']" % alb
    ])
    ThemeStories = Locator([
        lambda id: "table#%s  tr:not(:first-child)" % prefix(id, 'theme_'), 
        lambda aria_labelledby: "div.themes-div > table[aria-labelledby='%s']  tr:not(:first-child)" % aria_labelledby], list_=True)
    ThemeDescription = Locator(lambda id: "table#%s #theme_description > td > p" % prefix(id, 'theme_'))

    StoryInfo = Locator(lambda id: "#%s > td" % prefix(id, 'story_'), list_=True)
    StoryThumbnail = Locator(lambda id: "#%s img" % prefix(id, 'story_'))
    StoryRadioButton = Locator(lambda id: "#%s input" % prefix(id, 'story_'))
    StoryTitle = Locator(lambda id: "#%s > td:nth-child(3)" % prefix(id, 'story_'))

    DataLibraryMenuContainer = Locator('layers-menu', By.ID)
    DataLibraryMenuHeader = Locator("#layers-menu > label[for='layer-selection']")

    DataLibrarySearchContainer = Locator('search-content', By.ID)
    DataLibrarySearchIcon = Locator('span.layer-search-box-icon')
    DataLibrarySearchInput = Locator('layer-search-box', By.ID)
    DataLibrarySearchClearButton = Locator('layer-search-clear-icon', By.ID)
    DataLibraryClearActiveLayersButton = Locator('div.clearLayers')

    DataLibraryEmptySearchResultsMessage = Locator('layer-search-results-empty-msg', By.ID)
    DataLibrarySearchResultsContainer = Locator('layer-search-results', By.ID)
    DataLibrarySearchResultsCategories = Locator('#layer-search-results > div', list_=True)
    DataLibrarySearchResultsLabels = Locator("#layer-search-results > label", list_=True)

    DataLibrarySearchFoundCategories = Locator("#layer-search-results > div:not([style*='display: none']):not([style*='display:none'])", list_=True)
    DataLibrarySearchFoundLabels = Locator("#layer-search-results > label:not([style*='display: none']):not([style*='display:none'])", list_=True)

    DataLibrarySearchFoundLabelsBetween = Locator(lambda following, preceding: '//*[@id="layer-search-results"]/label[preceding-sibling::div[text()="%s"] and following-sibling::div[text()="%s"] and not(contains(@style, "display: none") or contains(@style, "display:none"))]' % (following, preceding), By.XPATH, list_=True)

    DataLibrarySearchFoundLabelsFollowing = Locator(lambda following: '//*[@id="layer-search-results"]/label[preceding-sibling::div[text()="%s"] and not(contains(@style, "display: none") or contains(@style, "display:none"))]' % following, By.XPATH, list_=True)

    DataLibrarySearchFoundLabelsPreceding = Locator(lambda preceding: '//*[@id="layer-search-results"]/label[following-sibling::div[text()="%s"] and not(contains(@style, "display: none") or contains(@style, "display:none"))]' % preceding, By.XPATH, list_=True)

    BaseLayersHeader = Locator('category-base-layers', By.ID)
    BaseLayerRows = Locator('#category-base-layers > tbody > tr', By.ID)
    BaseLayers = Locator('#category-base-layers > tbody > tr > td~label')
    BaseLayerDescriptions = Locator('#category-base-layers > tbody > tr > td~div.layer-description')
    
    CategoryMenu = Locator(["div.map-layer-div:not([style*='display: none']):not([style*='display:none']", 'div#featured-layers'])

    CategoryHeaders = Locator([
        "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > h3:not([style*='display: none']):not([style*='display:none']):not(:first-child)",
        "div#featured-layers > h3:not([style*='display: none']):not([style*='display:none']):not(:first-child)"],
        list_=True)

    CategoryHeadersAfter = Locator([
        lambda id : "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > h3#%s ~ h3:not([style*='display: none']):not([style*='display:none'])" % id,
        lambda ac : "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > h3[aria-controls='%s'] ~ h3:not([style*='display: none']):not([style*='display:none'])" % prefix(ac, 'category-'),
        lambda id : "div#featured-layers > h3#%s ~ h3:not([style*='display: none']):not([style*='display:none'])" % id,
        lambda ac : "div#featured-layers > h3[aria-controls='%s'] ~ h3:not([style*='display: none']):not([style*='display:none'])" % suffix(prefix(ac, 'category-'), '-featured')],
        list_=True)

    CategoryHeadersExcept = Locator([
        lambda id: "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > h3:not([style*='display: none']):not([style*='display:none']):not([aria-controls='category-base-layers']):not([id='%s'])" % id,
        lambda ac: "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > h3:not([style*='display: none']):not([style*='display:none']):not([aria-controls='category-base-layers']):not([aria-controls='%s'])" % prefix(ac, 'category-'),
        lambda id: "div#featured-layers > h3:not([style*='display: none']):not([style*='display:none']):not([aria-controls='category-base-layers']):not([id='%s'])" % id,
        lambda ac: "div#featured-layers > h3:not([style*='display: none']):not([style*='display:none']):not([aria-controls='category-base-layers']):not([aria-controls='%s'])" % suffix(prefix(ac, 'category-'), '-featured')],
        list_=True)

    CategoryTables = Locator([
        "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > table:not([style*='display: none']):not([style*='display:none']):not(:first-child)",
        "div#featured-layers > table:not([style*='display: none']):not([style*='display:none']):not(:first-child)"],
        list_=True)

    CategoryTablesAfter = Locator([
        lambda id : "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > table#%s ~ table:not([style*='display: none']):not([style*='display:none'])" % prefix(id, 'category-'),
        lambda alb : "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > table[aria-labelledby='%s'] ~ table:not([style*='display: none']):not([style*='display:none'])" % alb,
        lambda id : "div#featured-layers > table#%s ~ table:not([style*='display: none']):not([style*='display:none'])" % suffix(prefix(id, 'category-'), '-featured'),
        lambda alb : "div#featured-layers > table[aria-labelledby='%s'] ~ table:not([style*='display: none']):not([style*='display:none'])" % alb],
        list_=True)

    CategoryTablesExcept = Locator([
        lambda id: "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > table:not([style*='display: none']):not([style*='display:none']):not([id='category-base-layers']):not([id='%s'])" % prefix(id, 'category-'),
        lambda alb: "div.map-layer-div:not([style*='display: none']):not([style*='display:none']) > h3:not([style*='display: none']):not([style*='display:none']):not([id='category-base-layers']):not([aria-labelledby='%s'])" % alb,
        lambda id: "div#featured-layers > table:not([style*='display: none']):not([style*='display:none']):not([id='category-base-layers']):not([id='%s'])" % suffix(prefix(id, 'category-'), '-featured'),
        lambda alb: "div#featured-layers > h3:not([style*='display: none']):not([style*='display:none']):not([id='category-base-layers']):not([aria-labelledby='%s'])" % alb],
        list_=True)

    # FeaturedCategoryTables = Locator("div#featured-layers > table:not([style*='display: none']):not([style*='display:none'])", list_=True)

    CategoryHeader = Locator([
        lambda id: "h3#%s" % id,
        lambda ac: "h3[aria-controls='%s']" % prefix(ac, 'category-'),
        lambda ac: "h3[aria-controls='%s']" % suffix(prefix(ac, 'category-'), '-featured')
    ])

    CategoryTable = Locator([
        lambda id: "table#%s" % prefix(id, 'category-'),
        lambda id: "table#%s" % suffix(prefix(id, 'category-'), '-featured'),
        lambda alb: "table[aria-labelledby='%s']" % alb
    ])

    CategoryLayers = Locator([
        lambda id: "table#%s  tr" % prefix(id, 'category-'),
        lambda id: "table#%s  tr" % suffix(prefix(id, 'category-'), '-featured'),
        lambda alb: "table[aria-labelledby='%s'] tr" % alb], 
        list_=True)

    CategoryLabels = Locator([
        lambda id: "table#%s  tr > td > label" % prefix(id, 'category-'),
        lambda id: "table#%s  tr > td > label" % suffix(prefix(id, 'category-'), '-featured'),
        lambda alb: "table[aria-labelledby='%s'] tr > td > label" % alb,
        ], 
        list_=True)

    LayerLabel = Locator(lambda name: name, By.NAME)
    LayerInfo = Locator(lambda name: '//label[@name="%s"]/../../td' % name, By.XPATH, list_=True)
    LayerDescription = Locator(lambda name: '//label[@name="%s"]/../../td//div[@class="layer-description"]', By.XPATH)
    LayerCheckbox = Locator(lambda name: '//label[@name="%s"]/input' % name, By.XPATH)

    ShareViewContainer = Locator('div.shareView')
    ShareViewHeader = Locator('ui-id-5', By.ID)
    ShareViewCloseButton = Locator('button.close-share')
    ShareAsContainer = Locator("div.shareView > div[@role='tablist']")
    ShareAsLinkHeader = Locator('ui-id-1', By.ID)
    ShareAsLinkTable = Locator('table.share-link')
    ShareAsLinkInput = Locator('table.share-link input.shareurl')
    ShareAsLinkCopyButton = Locator('table.share-link div.shareurl-copy-text-button')
    ShareAsLinkCurrentWaypoint = Locator('table.share-link tr.presentation-mode-share-input:nth-child(1)')
    ShareAsLinkCurrentWaypointCheckbox = Locator('table.share-link input.waypoint-index')
    ShareAsLinkCurrentView = Locator('table.share-link tr.presentation-mode-share-input:nth-child(2)')
    ShareAsLinkCurrentViewCheckbox = Locator('table.share-link input.waypoint-only')
    ShareAsImageOrVideoHeader = Locator('ui-id-2', By.ID)
    ShareAsImageOrVideoTable = Locator('#ui-id-3 > table.share-thumbnail-tool')
    ShareAsImageOrVideoPreviewTable = Locator('#ui-id-3 > table.thumbnail-preview-copy-text-container')

    ShareAsImageOrVideoOutputDimensions = Locator('table.thumbnail-preview-copy-text-container tr:nth-child(1)')
    ShareAsImageOrVideoOutputDimensionsText = Locator('table.thumbnail-preview-copy-text-container tr:nth-child(1) > td:nth-child(1)')
    ShareAsImageOrVideoOutputDimensionsWidth = Locator('thumbnail-width', By.ID)
    ShareAsImageOrVideoOutputDimensionsHeight = Locator('thumbnail-height', By.ID)
    ShareAsImageOrVideoOutputDimensionsSwapButton = Locator("span.thumbnail-swap-selection-dimensions")

    ShareAsImageOrVideoStartingTime = Locator('table.thumbnail-preview-copy-text-container tr:nth-child(2)')
    ShareAsImageOrVideoStartingTimeText = Locator('table.thumbnail-preview-copy-text-container tr:nth-child(2) > td:nth-child(1)')
    ShareAsImageOrVideoStartingTimeInput = Locator('input.startingTimeSpinner')
    ShareAsImageOrVideoStartingTimeSpinnerUp = Locator('a.ui-spinner-up')
    ShareAsImageOrVideoStartingTimeSpinnerDown = Locator('a.ui-spinner-down')
    ShareAsImageOrVideoStartingTimeSetButton = Locator('span.thumbnail-set-start-time-from-timeline')

    ShareAsImageOrVideoEndingTime = Locator('table.thumbnail-preview-copy-text-container tr:nth-child(3)')
    ShareAsImageOrVideoEndingTimeText = Locator('table.thumbnail-preview-copy-text-container tr:nth-child(3) > td:nth-child(1)')
    ShareAsImageOrVideoEndingTimeInput = Locator('input.endingTimeSpinner')
    ShareAsImageOrVideoEndingTimeSpinnerUp = Locator('a.ui-spinner-up')
    ShareAsImageOrVideoEndingTimeSpinnerDown = Locator('a.ui-spinner-down')
    ShareAsImageOrVideoEndingTimeSetButton = Locator('span.thumbnail-set-end-time-from-timeline')

    StoryEditorContainer = Locator('div.story-editor')
    StoryEditorHeader = Locator("div.story-editor > div.wizard-head > p")
    StoryEditorCloseButton = Locator('div.story-editor > div.wizard-head > div.close')
    StoryEditorToolContainer = Locator('div.story-editor-intro')
    StoryEditorDescription = Locator('div.story-editor-intro > p')
    StoryEditorBeginButton = Locator('button.story-editor-start-button')
    StoryEditorLogoutButton = Locator('button.story-editor-logout-button')

    ZoomButtonsContainer = Locator('navControls', By.ID)
    ZoomInButton = Locator('button.zoomin')
    ZoomOutButton = Locator('button.zoomout')

    LegendContainer = Locator('layers-legend', By.ID)
    LegendContent = Locator('legend-content', By.ID)
    Legend = Locator("#legend-content > table > tbody > tr:not([style*='display: none']):not([style*='display:none'])")
    LegendText = Locator("#legend-content > table > tbody > tr:not([style*='display: none']):not([style*='display:none']) > td > div[style*='font-size']")

    ScaleBarContainer = Locator('scaleBar1_scaleBarContainer', By.ID)
    ScaleBarTopText = Locator('scaleBar1_scaleBarTop_txt', By.ID)
    ScaleBarBottomText = Locator('scaleBar1_scaleBarBot_txt', By.ID)
    ScaleBarIcon = Locator('scaleBar1_scaleBar_canvas', By.ID)

    ResumeExitStoryButtonsContainer = Locator("#timeMachine > div.player > div.annotations-resume-exit-container > table > tbody > tr")
    ResumeStoryButton = Locator('td.annotations-resume-button')
    ExitStoryButton = Locator('td.annotations-exit-button')

    AnnotationContainer = Locator('div.current-location-text-container')
    PreviousAnnotationButton = Locator('div.previous-annotation-location')
    NextAnnotationButton = Locator('div.next-annotation-location')
    AnnotationInfo = Locator('div.current-location-text')
    AnnotationTitle = Locator('div.current-location-text-title')
    AnnotationImage = Locator('div.current-location-text-picture')
    AnnotationText = Locator('div.current-location-text > p')
    AnnotationCitation = Locator('div.story-author-text')

    TimelineControl = Locator([
        "div.customControl:not([style*='display: none']):not([style*='display:none'])",
        "div.controls:not([style*='display: none']):not([style*='display:none'])"
    ])

    TimelinePlayPauseButton = Locator(['button.customPlay', 'button.playbackButton'])
    TimelineCurrentCaptureTime = Locator(['div.timeText', 'div.captureTimeMain'])
    TimelinePlaySpeedButtons = Locator([
        'button.customToggleSpeed', 
        'button.toggleSpeed'], 
        list_=True)
    TimelinePlaySpeedButtonsText = Locator([
        'button.customToggleSpeed > span',
        'button.toggleSpeed > span'], list_=True)

    CustomTimelineControl = Locator("div.customControl:not([style*='display: none']):not([style*='display:none'])")
    CustomPlayPauseButton = Locator('button.customPlay')
    CustomCurrentCaptureTime = Locator('div.timeText')
    CustomPlaySpeedButtons = Locator('button.customToggleSpeed', list_=True)
    CustomPlaySpeedButtonsText = Locator('button.customToggleSpeed > span', list_=True)
    CustomTimelineLeftText = Locator('div.timeTextLeft')
    CustomTimelineRightText = Locator('div.timeTextRight')
    CustomTimelineTicks = Locator('div.timeTickContainer', list_=True)

    DefaultTimelineControl = Locator("div.controls:not([style*='display: none']):not([style*='display:none'])")
    DefaultPlayPauseButton = Locator('button.playbackButton')
    DefaultCurrentCaptureTime = Locator('div.captureTimeMain')
    DefaultPlaySpeedButtons = Locator('button.toggleSpeed', list_=True)
    DefaultPlaySpeedButtonsText = Locator('button.toggleSpeed > span', list_=True)
    DefaultTimelineSlider = Locator('div.timelineSlider')
    DefaultTimelineCurrentFill = Locator('div.ui-slider-range')
    DefaultTimelineSliderHandle = Locator('span.ui-slider-handle')

    ThemeTitleContainer = Locator('theme-title-container', By.ID)
    WaypointsContainer = Locator('div.snaplapse_keyframe_list')
    Waypoints = Locator("div.snaplapse_keyframe_list > div[id*='timeMachine_snaplapse_keyframe_'] > div:first-child", list_=True)
    Waypoint = Locator([
        lambda id: 'div.snaplapse_keyframe_list_item > #%s' % id,
        lambda id: '#%s > div' % prefix(id, 'timeMachine_snaplapse_keyframe_')
    ])
    WaypointThumbnail = Locator([
        lambda id: suffix(prefix(id, 'timeMachine_snaplapse_keyframe_'), '_thumbnail'),
        lambda id: 'div.snaplapse_keyframe_list_item > #%s > img' % id],
        [By.ID, By.CSS])

    WaypointTitle = Locator([
        lambda id: suffix(prefix(id, 'timeMachine_snaplapse_keyframe_'), '_title'),
        lambda id: '#%s > div.snaplapse_keyframe_list_item_title' % id],
        [By.ID, By.CSS])

    MapLogosContainer = Locator('logosContainer', By.ID)
    EarthTimeProductLogo = Locator('productLogo', By.ID)
    ContributorsLogo = Locator('contributors', By.ID)

    BaseLayerCreditsContainer = Locator('baseLayerCreditContainer', By.ID)
    BaseLayerCreditHeader = Locator('baselayerCreditHeader', By.ID)
    BaseLayerCredits = Locator('baselayerCreditText', By.ID)
    BaseLayerCreditLogo = Locator('baselayerCreditLogo', By.ID)