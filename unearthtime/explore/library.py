from __future__ import annotations

from typing import Final

from .locator import Locator
from .query import By
from .._algae.strings import prefix, suffix

DISPLAYED: Final[str] = "not([style*='display: none']):not([style*='display:none'])"
XDISPLAYED: Final[str] = 'not(contains(@style, "display: none") or contains(@style, "display:none"))'


class LocatorReference(type):
    def __contains__(cls, key: str):
        return not key.startswith('_') and hasattr(cls, key)

    def __getitem__(cls, key: str):
        if not key.startswith('_') and hasattr(cls, key):
            return getattr(cls, key)

    def __iter__(cls):
        for locator in [loc for loc in dir(cls) if not loc.startswith('_')]:
            yield locator

    def count(cls):
        return len([locator for locator in dir(cls) if not locator.startswith('_')])


class Library(metaclass=LocatorReference):
    """Predefined locators for elements of an EarthTime page."""

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
        lambda id_: "h3#%s" % id_,
        lambda ac: "div.themes-div > h3[aria-controls='%s']" % prefix(ac, 'theme_')
    ])

    ThemeTable = Locator([
        lambda id_: "table#%s" % prefix(id_, 'theme_'),
        lambda alb: "div.themes-div > table[aria-labelledby='%s']" % alb
    ])

    ThemeStories = Locator([
        lambda id_: "table#%s  tr:not(:first-child)" % prefix(id_, 'theme_'),
        lambda aria_labelledby: "div.themes-div > table[aria-labelledby='%s']  tr:not(:first-child)" % aria_labelledby], list_=True)

    ThemeDescription = Locator(lambda id_: "table#%s #theme_description > td > p" % prefix(id_, 'theme_'))

    StoryInfo = Locator(lambda id_: "#%s > td" % prefix(id_, 'story_'), list_=True)
    StoryThumbnail = Locator(lambda id_: "#%s img" % prefix(id_, 'story_'))
    StoryRadioButton = Locator(lambda id_: "#%s input" % prefix(id_, 'story_'))
    StoryTitle = Locator(lambda id_: "#%s > td:nth-child(3)" % prefix(id_, 'story_'))

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

    DataLibrarySearchFoundCategories = Locator("#layer-search-results > div:%s" % DISPLAYED, list_=True)
    DataLibrarySearchFoundLabels = Locator("#layer-search-results > label:%s" % DISPLAYED, list_=True)

    DataLibrarySearchFoundLabelsBetween = Locator(lambda following, preceding: '//*[@id="layer-search-results"]/label[preceding-sibling::div[text()="%s"] and '
                                                                               'following-sibling::div[text()="%s"] and %s]' % (following, preceding, XDISPLAYED),
                                                  By.XPATH,
                                                  list_=True)

    DataLibrarySearchFoundLabelsAfter = Locator(lambda following: '//*[@id="layer-search-results"]/label[preceding-sibling::div[text()="%s"] and %s]' % (following, XDISPLAYED),
                                                By.XPATH,
                                                list_=True)

    DataLibrarySearchFoundLabelsBefore = Locator(lambda preceding: '//*[@id="layer-search-results"]/label[following-sibling::div[text()="%s"] and %s]' % (preceding, XDISPLAYED),
                                                 By.XPATH,
                                                 list_=True)

    BaseLayersHeader = Locator('category-base-layers', By.ID)
    BaseLayerRows = Locator('#category-base-layers > tbody > tr', By.ID)
    BaseLayers = Locator('#category-base-layers > tbody > tr > td~label')
    BaseLayerDescriptions = Locator('#category-base-layers > tbody > tr > td~div.layer-description')

    CategoryMenu = Locator(["div.map-layer-div:%s" % DISPLAYED, 'div#featured-layers'])

    CategoryHeaders = Locator([
        "div.map-layer-div:%s > h3:%s:not([aria-controls='category-base-layers'])" % (DISPLAYED, DISPLAYED),
        "div#featured-layers > h3:%s:not([aria-controls='category-base-layers'])" % DISPLAYED],
        list_=True)

    CategoryHeadersAfter = Locator([
        lambda id_: "div.map-layer-div:%s > h3#%s ~ h3:%s" % (DISPLAYED, id_, DISPLAYED),
        lambda ac: "div.map-layer-div:%s > h3[aria-controls='%s'] ~ h3:%s" % (DISPLAYED, (ac, 'category-'), DISPLAYED),
        lambda id_: "div#featured-layers > h3#%s ~ h3:%s" % (id_, DISPLAYED),
        lambda ac: "div#featured-layers > h3[aria-controls='%s'] ~ h3:%s" % (suffix(prefix(ac, 'category-'), '-featured'), DISPLAYED)],
        list_=True)

    CategoryHeadersExcept = Locator([
        lambda id_: "div.map-layer-div:%s > h3:%s:not([aria-controls='category-base-layers']):not([id='%s'])" % (DISPLAYED, DISPLAYED, id_),
        lambda ac: "div.map-layer-div:%s > h3:%s:not([aria-controls='category-base-layers']):not([aria-controls='%s'])" % (DISPLAYED, DISPLAYED, prefix(ac, 'category-')),
        lambda id_: "div#featured-layers > h3:%s:not([aria-controls='category-base-layers']):not([id='%s'])" % (DISPLAYED, id_),
        lambda ac: "div#featured-layers > h3:%s:not([aria-controls='category-base-layers']):not([aria-controls='%s'])" % (DISPLAYED, suffix(prefix(ac, 'category-'), '-featured'))],
        list_=True)

    CategoryTables = Locator([
        "div.map-layer-div:%s > table:not(:first-child)" % DISPLAYED,
        "div#featured-layers > table:not(:first-child)"],
        list_=True)

    CategoryTablesAfter = Locator([
        lambda id_: "div.map-layer-div:%s > table#%s ~ table" % (DISPLAYED, prefix(id_, 'category-')),
        lambda alb: "div.map-layer-div:%s > table[aria-labelledby='%s'] ~ table" % (DISPLAYED, alb),
        lambda id_: "div#featured-layers > table#%s ~ table" % suffix(prefix(id_, 'category-'), '-featured'),
        lambda alb: "div#featured-layers > table[aria-labelledby='%s'] ~ table" % alb],
        list_=True)

    CategoryTablesExcept = Locator([
        lambda id_: "div.map-layer-div:%s > table:not([id='category-base-layers']):not([id='%s'])" % (DISPLAYED, prefix(id_, 'category-')),
        lambda alb: "div.map-layer-div:%s > table:%s:not([id='category-base-layers']):not([aria-labelledby='%s'])" % (DISPLAYED, DISPLAYED, alb),
        lambda id_: "div#featured-layers > table:not([id='category-base-layers']):not([id='%s'])" % suffix(prefix(id_, 'category-'), '-featured'),
        lambda alb: "div#featured-layers > table:%s:not([id='category-base-layers']):not([aria-labelledby='%s'])" % (DISPLAYED, alb)],
        list_=True)

    LayerLabels = Locator([
        "div.map-layer-div:%s > table:not(:first-child) tr > td > label" % DISPLAYED,
        "div#featured-layers > table:not([id='category-base-layers']) tr > td > label"
    ])

    LayerCheckboxes = Locator([
        "div.map-layer-div:%s > table:not([id='category-base-layers']) tr > td > label > input" % DISPLAYED,
        "div#featured-layers > table:not([id='category-base-layers']) tr > td > label > input"
    ],
        list_=True)

    CheckedLayerCheckboxes = Locator([
        "div.map-layer-div:%s > table:not([id='category-base-layers']) label > input:checked" % DISPLAYED,
        "div#featured-layers > table:not([id='category-base-layers']) label > input:checked"
    ])

    FeaturedLayersShowMoreButton = Locator("div#show-more-layers:not([class='active'])")
    FeaturedLayersShowLessButton = Locator("div#show-more-layers[class='active']")

    CategoryHeader = Locator([
        lambda id_: "h3#%s" % id_,
        lambda ac: "h3[aria-controls='%s']" % prefix(ac, 'category-'),
        lambda ac: "h3[aria-controls='%s']" % suffix(prefix(ac, 'category-'), '-featured')
    ])

    CategoryTable = Locator([
        lambda id_: "table#%s" % prefix(id_, 'category-'),
        lambda id_: "table#%s" % suffix(prefix(id_, 'category-'), '-featured'),
        lambda alb: "table[aria-labelledby='%s']" % alb
    ])

    CategoryLayers = Locator([
        lambda id_: "table#%s  tr" % prefix(id_, 'category-'),
        lambda id_: "table#%s  tr" % suffix(prefix(id_, 'category-'), '-featured'),
        lambda alb: "table[aria-labelledby='%s'] tr" % alb],
        list_=True)

    CategoryLabels = Locator([
        lambda id_: "table#%s  tr > td > label" % prefix(id_, 'category-'),
        lambda id_: "table#%s  tr > td > label" % suffix(prefix(id_, 'category-'), '-featured'),
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
    Legend = Locator("#legend-content > table > tbody > tr:%s" % DISPLAYED)
    LegendText = Locator("#legend-content > table > tbody > tr:%s > td > div[style*='font-size']" % DISPLAYED)

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
        "div.customControl:%s" % DISPLAYED,
        "div.controls:%s" % DISPLAYED
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

    CustomTimelineControl = Locator("div.customControl:%s" % DISPLAYED)
    CustomPlayPauseButton = Locator('button.customPlay')
    CustomCurrentCaptureTime = Locator('div.timeText')
    CustomPlaySpeedButtons = Locator('button.customToggleSpeed', list_=True)
    CustomPlaySpeedButtonsText = Locator('button.customToggleSpeed > span', list_=True)
    CustomTimelineLeftText = Locator('div.timeTextLeft')
    CustomTimelineRightText = Locator('div.timeTextRight')
    CustomTimelineTicks = Locator('div.timeTickContainer', list_=True)

    DefaultTimelineControl = Locator("div.controls:%s" % DISPLAYED)
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
        lambda id_: 'div.snaplapse_keyframe_list_item > #%s' % id_,
        lambda id_: '#%s > div' % prefix(id_, 'timeMachine_snaplapse_keyframe_')
    ])
    WaypointThumbnail = Locator([
        lambda id_: suffix(prefix(id_, 'timeMachine_snaplapse_keyframe_'), '_thumbnail'),
        lambda id_: 'div.snaplapse_keyframe_list_item > #%s > img' % id_],
        [By.ID, By.CSS])

    WaypointTitle = Locator([
        lambda id_: suffix(prefix(id_, 'timeMachine_snaplapse_keyframe_'), '_title'),
        lambda id_: '#%s > div.snaplapse_keyframe_list_item_title' % id_],
        [By.ID, By.CSS])

    MapLogosContainer = Locator('logosContainer', By.ID)
    EarthTimeProductLogo = Locator('productLogo', By.ID)
    ContributorsLogo = Locator('contributors', By.ID)

    BaseLayerCreditsContainer = Locator('baseLayerCreditContainer', By.ID)
    BaseLayerCreditHeader = Locator('baselayerCreditHeader', By.ID)
    BaseLayerCredits = Locator('baselayerCreditText', By.ID)
    BaseLayerCreditLogo = Locator('baselayerCreditLogo', By.ID)
