from __future__ import annotations

from typing import Final

from .locator import Locator
from .query import By
from .._algae.strings import prefix, suffix

NOT_BASE_MAPS_CSS: Final[str] = "not([aria-controls='category-base-layers'])"
NOT_DISPLAYED_CSS: Final[str] = "not([style*='display: none']):not([style*='display:none'])"
NOT_DISPLAYED_XPATH: Final[str] = 'not(contains(@style, "display: none") or contains(@style, "display:none"))'


class Library:
    """Predefined locators for elements of an EarthTime page."""

    StandardLocators = {
        'TopNavigation': Locator('top-nav', By.ID),
        'EarthTimeLogo': Locator('menu-logo', By.ID),
        'StoriesMenu': Locator('stories-menu-choice', By.ID),
        'DataLibraryMenu': Locator('layers-menu-choice', By.ID),
        'ShareButton': Locator('share-menu-choice', By.ID),
        'StoryEditorButton': Locator('story-editor-menu-choice', By.ID),
        'DataPanes': Locator('timeMachine_timelapse_dataPanes', By.ID),
        'ExtrasContent': Locator('[aria-describedby="extras-content-container"]'),
        'ExtrasContentCloseButton': Locator('[aria-describedby="extras-conent-container"] button[title="Close"]'),

        'LocationSearchContainer': Locator('div.location_search_div', By.ID),
        'LocationSearchIcon': Locator('location_search_icon', By.ID),
        'LocationSearchInput': Locator('location_search', By.ID),
        'LocationSearchClearButton': Locator('location_search_clear_icon', By.ID),

        'StoriesMenuContainer': Locator('theme-menu', By.ID),
        'StoriesMenuHeader': Locator("#theme-menu > label[for='theme-selection']"),
        'ThemeMenu': Locator('div.themes-div'),
        'ThemeHeaders': Locator("div.themes-div > h3[data-enabled='true']", list_=True),
        'ThemeTables': Locator("div.themes-div > table[data-enabled='true']", list_=True),

        'ThemeHeader': Locator([
            lambda id_: f"h3#{id_}",
            lambda ac: f"div.themes-div > h3[aria-controls='{prefix(ac, 'theme_')}']"
        ]),

        'ThemeTable': Locator([
            lambda id_: f"table#{prefix(id_, 'theme_')}",
            lambda alb: f"div.themes-div > table[aria-labelledby='{alb}']"
        ]),

        'ThemeStories': Locator([
            lambda id_: f"table#{prefix(id_, 'theme_')}  tr:not(:first-child)",
            lambda alb: f"div.themes-div > table[aria-labelledby='{alb}']  tr:not(:first-child)"], list_=True),

        'ThemeDescription': Locator(lambda id_: f"table#{prefix(id_, 'theme_')} #theme_description > td > p"),

        'StoryInfo': Locator(lambda id_: f"#{prefix(id_, 'story_')} > td", list_=True),
        'StoryThumbnail': Locator(lambda id_: f"#{prefix(id_, 'story_')} img"),
        'StoryRadioButton': Locator(lambda id_: f"#{prefix(id_, 'story_')} input"),
        'StoryTitle': Locator(lambda id_: f"#{prefix(id_, 'story_')} > td:nth-child(3)"),

        'DataLibraryMenuContainer': Locator('layers-menu', By.ID),
        'DataLibraryMenuHeader': Locator("#layers-menu > label[for='layer-selection']"),

        'DataLibrarySearchContainer': Locator('search-content', By.ID),
        'DataLibrarySearchIcon': Locator('span.layer-search-box-icon'),
        'DataLibrarySearchInput': Locator('layer-search-box', By.ID),
        'DataLibrarySearchClearButton': Locator('layer-search-clear-icon', By.ID),
        'DataLibraryClearActiveLayersButton': Locator('div.clearLayers'),

        'DataLibraryEmptySearchResultsMessage': Locator('layer-search-results-empty-msg', By.ID),
        'DataLibrarySearchResultsContainer': Locator('layer-search-results', By.ID),
        'DataLibrarySearchResultsCategories': Locator('#layer-search-results > div', list_=True),
        'DataLibrarySearchResultsLabels': Locator("#layer-search-results > label", list_=True),

        'DataLibrarySearchFoundCategories': Locator(f"#layer-search-results > div:{NOT_DISPLAYED_CSS}", list_=True),
        'DataLibrarySearchFoundLabels': Locator(f"#layer-search-results > label:{NOT_DISPLAYED_CSS}", list_=True),

        'DataLibrarySearchFoundLabelsBetween': Locator(lambda after, before: f'//*[@id="layer-search-results"]/label[preceding-sibling::div[text()="{after}"] and '
                                                                             f'following-sibling::div[text()="{before}"] and {NOT_DISPLAYED_XPATH}]',
                                                       By.XPATH,
                                                       list_=True),

        'DataLibrarySearchFoundLabelsAfter': Locator(lambda after: f'//*[@id="layer-search-results"]/label[preceding-sibling::div[text()="{after}"] and {NOT_DISPLAYED_XPATH}]',
                                                     By.XPATH,
                                                     list_=True),

        'DataLibrarySearchFoundLabelsBefore': Locator(lambda before: f'//*[@id="layer-search-results"]/label[following-sibling::div[text()="{before}"] and {NOT_DISPLAYED_XPATH}]',
                                                      By.XPATH,
                                                      list_=True),

        'BaseLayersHeader': Locator('category-base-layers', By.ID),
        'BaseLayerRows': Locator('#category-base-layers > tbody > tr', By.ID),
        'BaseLayers': Locator('#category-base-layers > tbody > tr > td~label'),
        'BaseLayerDescriptions': Locator('#category-base-layers > tbody > tr > td~div.layer-description'),

        'CategoryMenu': Locator([f"div.map-layer-div:{NOT_DISPLAYED_CSS}", 'div#featured-layers']),

        'CategoryHeaders': Locator([
            f"div.map-layer-div:{NOT_DISPLAYED_CSS} > h3:{NOT_DISPLAYED_CSS}:{NOT_BASE_MAPS_CSS}",
            f"div#featured-layers > h3:{NOT_DISPLAYED_CSS}:{NOT_BASE_MAPS_CSS}"],
            list_=True),

        'CategoryHeadersAfter': Locator([
            lambda id_: f"div.map-layer-div:{NOT_DISPLAYED_CSS} > h3#{id} ~ h3:{NOT_DISPLAYED_CSS}",
            lambda ac: f"div.map-layer-div:{NOT_DISPLAYED_CSS} > h3[aria-controls='{(ac, 'category-')}'] ~ h3:{NOT_DISPLAYED_CSS}",
            lambda id_: f"div#featured-layers > h3#{id_} ~ h3:{NOT_DISPLAYED_CSS}",
            lambda ac: f"div#featured-layers > h3[aria-controls='{suffix(prefix(ac, 'category-'), '-featured')}'] ~ h3:{NOT_DISPLAYED_CSS}"],
            list_=True),

        'CategoryHeadersExcept': Locator([
            lambda id_: f"div.map-layer-div:{NOT_DISPLAYED_CSS} > h3:{NOT_DISPLAYED_CSS}:{NOT_BASE_MAPS_CSS}:not([id='{id_}'])",
            lambda ac: f"div.map-layer-div:{NOT_DISPLAYED_CSS} > h3:{NOT_DISPLAYED_CSS}:{NOT_BASE_MAPS_CSS}:not([aria-controls='{prefix(ac, 'category-')}'])",
            lambda id_: f"div#featured-layers > h3:{NOT_DISPLAYED_CSS}:{NOT_BASE_MAPS_CSS}:not([id='{id_}'])",
            lambda ac: f"div#featured-layers > h3:{NOT_DISPLAYED_CSS}:{NOT_BASE_MAPS_CSS}:not([aria-controls='{suffix(prefix(ac, 'category-'), '-featured')}'])"],
            list_=True),

        'CategoryTables': Locator([
            f"div.map-layer-div:{NOT_DISPLAYED_CSS} > table:not(:first-child)",
            "div#featured-layers > table:not(:first-child)"],
            list_=True),

        'CategoryTablesAfter': Locator([
            lambda id_: f"div.map-layer-div:{NOT_DISPLAYED_CSS} > table#{prefix(id_, 'category-')} ~ table",
            lambda alb: f"div.map-layer-div:{NOT_DISPLAYED_CSS} > table[aria-labelledby='{alb}'] ~ table",
            lambda id_: f"div#featured-layers > table#{suffix(prefix(id_, 'category-'), '-featured')} ~ table",
            lambda alb: f"div#featured-layers > table[aria-labelledby='{alb}'] ~ table"],
            list_=True),

        'CategoryTablesExcept': Locator([
            lambda id_: f"div.map-layer-div:{NOT_DISPLAYED_CSS} > table:not([id='category-base-layers']):not([id='{prefix(id_, 'category-')}'])",
            lambda alb: f"div.map-layer-div:{NOT_DISPLAYED_CSS} > table:{NOT_DISPLAYED_CSS}:not([id='category-base-layers']):not([aria-labelledby='{alb}'])",
            lambda id_: f"div#featured-layers > table:not([id='category-base-layers']):not([id='{suffix(prefix(id_, 'category-'), '-featured')}'])",
            lambda alb: f"div#featured-layers > table:{NOT_DISPLAYED_CSS}:not([id='category-base-layers']):not([aria-labelledby='{alb}'])"],
            list_=True),

        'LayerLabels': Locator([
            f"div.map-layer-div:{NOT_DISPLAYED_CSS} > table:not(:first-child) tr > td > label",
            "div#featured-layers > table:not([id='category-base-layers']) tr > td > label"
        ]),

        'LayerCheckboxes': Locator([
            f"div.map-layer-div:{NOT_DISPLAYED_CSS} > table:not([id='category-base-layers']) tr > td > label > input",
            "div#featured-layers > table:not([id='category-base-layers']) tr > td > label > input"
        ],
            list_=True),

        'CheckedLayerCheckboxes': Locator([
            f"div.map-layer-div:{NOT_DISPLAYED_CSS} > table:not([id='category-base-layers']) label > input:checked",
            "div#featured-layers > table:not([id='category-base-layers']) label > input:checked"
        ]),

        'FeaturedLayersShowMoreButton': Locator("div#show-more-layers:not([class='active'])"),
        'FeaturedLayersShowLessButton': Locator("div#show-more-layers[class='active']"),

        'CategoryHeader': Locator([
            lambda id_: f"h3#{id_}",
            lambda ac: f"h3[aria-controls='{prefix(ac, 'category-')}']",
            lambda ac: f"h3[aria-controls='{suffix(prefix(ac, 'category-'), '-featured')}']"
        ]),

        'CategoryTable': Locator([
            lambda id_: f"table#{prefix(id_, 'category-')}",
            lambda id_: f"table#{suffix(prefix(id_, 'category-'), '-featured')}",
            lambda alb: f"table[aria-labelledby='{alb}']"
        ]),

        'CategoryLayers': Locator([
            lambda id_: f"table#{prefix(id_, 'category-')}  tr",
            lambda id_: f"table#{suffix(prefix(id_, 'category-'), '-featured')}  tr",
            lambda alb: f"table[aria-labelledby='{alb}'] tr"],
            list_=True),

        'CategoryLabels': Locator([
            lambda id_: f"table#{prefix(id_, 'category-')}  tr > td > label",
            lambda id_: f"table#{suffix(prefix(id_, 'category-'), '-featured')}  tr > td > label",
            lambda alb: f"table[aria-labelledby='{alb}'] tr > td > label",
        ],
            list_=True),

        'LayerLabel': Locator(lambda name: name, By.NAME),
        'LayerInfo': Locator(lambda name: f'//label[@name="{name}"]/../../td', By.XPATH, list_=True),
        'LayerDescription': Locator(lambda name: f'//label[@name="{name}"]/../../td//div[@class="layer-description"]', By.XPATH),
        'LayerCheckbox': Locator(lambda name: f'//label[@name="{name}"]/input', By.XPATH),

        'ShareViewContainer': Locator('div.shareView'),
        'ShareViewHeader': Locator('ui-id-5', By.ID),
        'ShareViewCloseButton': Locator('button.close-share'),
        'ShareAsContainer': Locator("div.shareView > div[@role='tablist']"),
        'ShareAsLinkHeader': Locator('ui-id-1', By.ID),
        'ShareAsLinkTable': Locator('table.share-link'),
        'ShareAsLinkInput': Locator('table.share-link input.shareurl'),
        'ShareAsLinkCopyButton': Locator('table.share-link div.shareurl-copy-text-button'),
        'ShareAsLinkCurrentWaypoint': Locator('table.share-link tr.presentation-mode-share-input:nth-child(1)'),
        'ShareAsLinkCurrentWaypointCheckbox': Locator('table.share-link input.waypoint-index'),
        'ShareAsLinkCurrentView': Locator('table.share-link tr.presentation-mode-share-input:nth-child(2)'),
        'ShareAsLinkCurrentViewCheckbox': Locator('table.share-link input.waypoint-only'),
        'ShareAsImageOrVideoHeader': Locator('ui-id-2', By.ID),
        'ShareAsImageOrVideoTable': Locator('#ui-id-3 > table.share-thumbnail-tool'),
        'ShareAsImageOrVideoPreviewTable': Locator('#ui-id-3 > table.thumbnail-preview-copy-text-container'),

        'ShareAsImageOrVideoOutputDimensions': Locator('table.thumbnail-preview-copy-text-container tr:nth-child(1)'),
        'ShareAsImageOrVideoOutputDimensionsText': Locator('table.thumbnail-preview-copy-text-container tr:nth-child(1) > td:nth-child(1)'),
        'ShareAsImageOrVideoOutputDimensionsWidth': Locator('thumbnail-width', By.ID),
        'ShareAsImageOrVideoOutputDimensionsHeight': Locator('thumbnail-height', By.ID),
        'ShareAsImageOrVideoOutputDimensionsSwapButton': Locator("span.thumbnail-swap-selection-dimensions"),

        'ShareAsImageOrVideoStartingTime': Locator('table.thumbnail-preview-copy-text-container tr:nth-child(2)'),
        'ShareAsImageOrVideoStartingTimeText': Locator('table.thumbnail-preview-copy-text-container tr:nth-child(2) > td:nth-child(1)'),
        'ShareAsImageOrVideoStartingTimeInput': Locator('input.startingTimeSpinner'),
        'ShareAsImageOrVideoStartingTimeSpinnerUp': Locator('a.ui-spinner-up'),
        'ShareAsImageOrVideoStartingTimeSpinnerDown': Locator('a.ui-spinner-down'),
        'ShareAsImageOrVideoStartingTimeSetButton': Locator('span.thumbnail-set-start-time-from-timeline'),

        'ShareAsImageOrVideoEndingTime': Locator('table.thumbnail-preview-copy-text-container tr:nth-child(3)'),
        'ShareAsImageOrVideoEndingTimeText': Locator('table.thumbnail-preview-copy-text-container tr:nth-child(3) > td:nth-child(1)'),
        'ShareAsImageOrVideoEndingTimeInput': Locator('input.endingTimeSpinner'),
        'ShareAsImageOrVideoEndingTimeSpinnerUp': Locator('a.ui-spinner-up'),
        'ShareAsImageOrVideoEndingTimeSpinnerDown': Locator('a.ui-spinner-down'),
        'ShareAsImageOrVideoEndingTimeSetButton': Locator('span.thumbnail-set-end-time-from-timeline'),

        'StoryEditorContainer': Locator('div.story-editor'),
        'StoryEditorHeader': Locator("div.story-editor > div.wizard-head > p"),
        'StoryEditorCloseButton': Locator('div.story-editor > div.wizard-head > div.close'),
        'StoryEditorToolContainer': Locator('div.story-editor-intro'),
        'StoryEditorDescription': Locator('div.story-editor-intro > p'),
        'StoryEditorBeginButton': Locator('button.story-editor-start-button'),
        'StoryEditorLogoutButton': Locator('button.story-editor-logout-button'),

        'ZoomButtonsContainer': Locator('navControls', By.ID),
        'ZoomInButton': Locator('button.zoomin'),

        'LegendContainer': Locator('layers-legend', By.ID),
        'LegendContent': Locator('legend-content', By.ID),
        'Legend': Locator(f"#legend-content > table > tbody > tr:{NOT_DISPLAYED_CSS}"),
        'LegendText': Locator(f"#legend-content > table > tbody > tr:{NOT_DISPLAYED_CSS} > td > div[style*='font-size']"),

        'ScaleBarContainer': Locator('scaleBar1_scaleBarContainer', By.ID),
        'ScaleBarTopText': Locator('scaleBar1_scaleBarTop_txt', By.ID),
        'ScaleBarBottomText': Locator('scaleBar1_scaleBarBot_txt', By.ID),
        'ScaleBarIcon': Locator('scaleBar1_scaleBar_canvas', By.ID),

        'ResumeExitStoryButtonsContainer': Locator("#timeMachine > div.player > div.annotations-resume-exit-container > table > tbody > tr"),
        'ResumeStoryButton': Locator('td.annotations-resume-button'),
        'ExitStoryButton': Locator('td.annotations-exit-button'),

        'AnnotationContainer': Locator('div.current-location-text-container'),
        'PreviousAnnotationButton': Locator('div.previous-annotation-location'),
        'NextAnnotationButton': Locator('div.next-annotation-location'),
        'AnnotationInfo': Locator('div.current-location-text'),
        'AnnotationTitle': Locator('div.current-location-text-title'),
        'AnnotationImage': Locator('div.current-location-text-picture'),
        'AnnotationText': Locator('div.current-location-text > p'),
        'AnnotationCitation': Locator('div.story-author-text'),

        'TimelineControl': Locator([
            f"div.customControl:{NOT_DISPLAYED_CSS}",
            f"div.controls:{NOT_DISPLAYED_CSS}"
        ]),

        'TimelinePlayPauseButton': Locator(['button.customPlay', 'button.playbackButton']),
        'TimelineCurrentCaptureTime': Locator(['div.timeText', 'div.captureTimeMain']),
        'TimelinePlaySpeedButtons': Locator([
            'button.customToggleSpeed',
            'button.toggleSpeed'],
            list_=True),
        'TimelinePlaySpeedButtonsText': Locator([
            'button.customToggleSpeed > span',
            'button.toggleSpeed > span'], list_=True),

        'CustomTimelineControl': Locator(f"div.customControl:{NOT_DISPLAYED_CSS}"),
        'CustomPlayPauseButton': Locator('button.customPlay'),
        'CustomCurrentCaptureTime': Locator('div.timeText'),
        'CustomPlaySpeedButtons': Locator('button.customToggleSpeed', list_=True),
        'CustomPlaySpeedButtonsText': Locator('button.customToggleSpeed > span', list_=True),
        'CustomTimelineLeftText': Locator('div.timeTextLeft'),
        'CustomTimelineRightText': Locator('div.timeTextRight'),
        'CustomTimelineTicks': Locator('div.timeTickContainer', list_=True),

        'DefaultTimelineControl': Locator(f"div.controls:{NOT_DISPLAYED_CSS}"),
        'DefaultPlayPauseButton': Locator('button.playbackButton'),
        'DefaultCurrentCaptureTime': Locator('div.captureTimeMain'),
        'DefaultPlaySpeedButtons': Locator('button.toggleSpeed', list_=True),
        'DefaultPlaySpeedButtonsText': Locator('button.toggleSpeed > span', list_=True),
        'DefaultTimelineSlider': Locator('div.timelineSlider'),
        'DefaultTimelineCurrentFill': Locator('div.ui-slider-range'),
        'DefaultTimelineSliderHandle': Locator('span.ui-slider-handle'),

        'ThemeTitleContainer': Locator('theme-title-container', By.ID),
        'WaypointsContainer': Locator('div.snaplapse_keyframe_list'),
        'Waypoints': Locator("div.snaplapse_keyframe_list > div[id*='timeMachine_snaplapse_keyframe_'] > div:first-child", list_=True),
        'Waypoint': Locator([
            lambda id_: f'div.snaplapse_keyframe_list_item > #{id_}',
            lambda id_: f'#{prefix(id_, "timeMachine_snaplapse_keyframe_")} > div',
        ]),
        'WaypointThumbnail': Locator([
            lambda id_: suffix(prefix(id_, 'timeMachine_snaplapse_keyframe_'), '_thumbnail'),
            lambda id_: f'div.snaplapse_keyframe_list_item > #{id_} > img'],
            [By.ID, By.CSS]),

        'WaypointTitle': Locator([
            lambda id_: suffix(prefix(id_, 'timeMachine_snaplapse_keyframe_'), '_title'),
            lambda id_: f'#{id_} > div.snaplapse_keyframe_list_item_title'],
            [By.ID, By.CSS]),

        'MapLogosContainer': Locator('logosContainer', By.ID),
        'EarthTimeProductLogo': Locator('productLogo', By.ID),
        'ContributorsLogo': Locator('contributors', By.ID),

        'BaseLayerCreditsContainer': Locator('baseLayerCreditContainer', By.ID),
        'BaseLayerCreditHeader': Locator('baselayerCreditHeader', By.ID),
        'BaseLayerCredits': Locator('baselayerCreditText', By.ID),
        'BaseLayerCreditLogo': Locator('baselayerCreditLogo', By.ID)
    }