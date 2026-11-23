import { useRef, useState } from 'react'
import type { DataframeConfig } from '../../config/defaultPlotConfig'
import { DEFAULT_DATAFRAME } from '../../config/settingsSections'
import { useI18n } from '../../uiTranslations'
import { formatAspectRatio, isSameAspectRatio, parseAspectRatio, parsePositiveInteger } from '../../utils/appState'
import { useAttributionUnlocked } from '../../utils/attributionKey'
import { LOGO_FILE_ACCEPT, MAX_LOGO_BYTES, setCustomLogo, useCustomLogo, type LogoFileProblem } from '../../utils/customLogo'
import { Field, PresetInput, Toggle, Switch } from '../common/AppControls'

type Props = {
  activeDataframe: DataframeConfig
  patchActiveDataframe: (patch: (current: DataframeConfig) => DataframeConfig) => void
}

const ASPECT_RATIO_PRESETS: Array<{ value: [number, number]; label: string }> = [
  { value: [1, 1], label: '1:1' },
  { value: [4, 3], label: '4:3' },
  { value: [3, 2], label: '3:2' },
  { value: [16, 9], label: '16:9' },
]
const RESOLUTION_PRESETS = [100, 150, 300, 600].map((value) => ({ value, label: String(value) }))

/** Upload of an own watermark logo next to the switch; the icon turns into the logo's name with a button to drop it again. */
function CustomLogoControl() {
  const { t } = useI18n()
  const logo = useCustomLogo()
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [problem, setProblem] = useState<LogoFileProblem | null>(null)
  const buttonClass = 'inline-flex h-9 w-9 items-center justify-center rounded-md border border-zinc-300 bg-white text-zinc-600 shadow-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800'
  const choose = async (file: File | undefined) => {
    if (!file) return
    try {
      await setCustomLogo(file)
      setProblem(null)
    } catch (error) {
      setProblem(error instanceof Error ? error.message as LogoFileProblem : 'storage')
    }
  }
  return (
    <>
      <input ref={inputRef} type="file" accept={LOGO_FILE_ACCEPT} className="hidden" onChange={(event) => { void choose(event.target.files?.[0]); event.target.value = '' }} />
      <button type="button" className={buttonClass} title={logo ? t('customLogoReplace', { name: logo.name }) : t('customLogoUpload')} aria-label={t('customLogoUpload')} onClick={() => inputRef.current?.click()}>
        <svg viewBox="0 0 24 24" className={`h-4 w-4 ${logo ? 'text-brand-600' : ''}`} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M12 16V4M7 9l5-5 5 5M4 20h16" />
        </svg>
      </button>
      {logo && (
        <button type="button" className={buttonClass} title={t('customLogoRemove', { name: logo.name })} aria-label={t('customLogoRemove', { name: logo.name })} onClick={() => { void setCustomLogo(null); setProblem(null) }}>
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      )}
      {problem && <span role="alert" className="basis-full text-xs text-red-600 dark:text-red-400">{t(problem === 'type' ? 'customLogoBadType' : problem === 'size' ? 'customLogoTooLarge' : 'customLogoNotStored', { kb: MAX_LOGO_BYTES / 1000 })}</span>}
    </>
  )
}

/** Shape, background and file of the plot image; shared by all frames of the dataframe. */
export function ImageOutputSection({ activeDataframe, patchActiveDataframe }: Props) {
  const { t } = useI18n()
  const isPng = activeDataframe.fileformat === 'png'
  const attributionUnlocked = useAttributionUnlocked()
  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap gap-4">
        <Field label={t('aspectRatio')} jsonPath="dataframes[i].image_ratio" level="default" changed={!isSameAspectRatio(activeDataframe.aspectRatio, DEFAULT_DATAFRAME.aspectRatio)} onReset={() => patchActiveDataframe((current) => ({ ...current, aspectRatio: DEFAULT_DATAFRAME.aspectRatio }))}>
          <PresetInput
            ariaLabel={t('aspectRatio')}
            presets={ASPECT_RATIO_PRESETS}
            value={activeDataframe.aspectRatio}
            isSame={isSameAspectRatio}
            format={formatAspectRatio}
            parse={parseAspectRatio}
            onChange={(aspectRatio) => patchActiveDataframe((current) => ({ ...current, aspectRatio }))}
          />
        </Field>
        <Field label={t('fileFormat')} jsonPath="dataframes[i].fileformat" level="default" changed={activeDataframe.fileformat !== DEFAULT_DATAFRAME.fileformat} onReset={() => patchActiveDataframe((current) => ({ ...current, fileformat: DEFAULT_DATAFRAME.fileformat }))}>
          <Toggle<'svg' | 'png'>
            ariaLabel={t('fileFormat')}
            value={activeDataframe.fileformat}
            onChange={(fileformat) => patchActiveDataframe((current) => ({ ...current, fileformat }))}
            options={[{ value: 'svg', label: 'SVG' }, { value: 'png', label: 'PNG' }]}
          />
        </Field>
        <Field label={t('resolutionDpi')} jsonPath="dataframes[i].resolution" level="default" changed={activeDataframe.resolution !== DEFAULT_DATAFRAME.resolution} onReset={() => patchActiveDataframe((current) => ({ ...current, resolution: DEFAULT_DATAFRAME.resolution }))} hint={t('dpiHint')}>
          <PresetInput
            ariaLabel={t('resolutionDpi')}
            presets={RESOLUTION_PRESETS}
            value={activeDataframe.resolution}
            isSame={(a, b) => a === b}
            format={String}
            parse={parsePositiveInteger}
            onChange={(resolution) => patchActiveDataframe((current) => ({ ...current, resolution }))}
            disabled={!isPng}
          />
        </Field>
      </div>
      {/* The switches in one row; copyright and watermark only with the attribution key. */}
      <div className="grid grid-cols-2 gap-4 @lg:grid-cols-4">
        <Field label={t('DarkMode')} jsonPath="dataframes[i].dark_mode" level="default" changed={activeDataframe.darkMode !== DEFAULT_DATAFRAME.darkMode} onReset={() => patchActiveDataframe((current) => ({ ...current, darkMode: DEFAULT_DATAFRAME.darkMode }))}>
          <Switch checked={activeDataframe.darkMode} label={t('DarkMode')} onChange={(darkMode) => patchActiveDataframe((current) => ({ ...current, darkMode }))} />
        </Field>
        <Field label={t('transparent')} jsonPath="dataframes[i].transparent" level="default" changed={activeDataframe.transparent !== DEFAULT_DATAFRAME.transparent} onReset={() => patchActiveDataframe((current) => ({ ...current, transparent: DEFAULT_DATAFRAME.transparent }))}>
          <Switch checked={activeDataframe.transparent} label={t('transparent')} onChange={(transparent) => patchActiveDataframe((current) => ({ ...current, transparent }))} />
        </Field>
        {attributionUnlocked && (
          <>
            <Field label={t('watermark')} jsonPath="dataframes[i].watermark" level="default" changed={activeDataframe.watermark !== DEFAULT_DATAFRAME.watermark} onReset={() => patchActiveDataframe((current) => ({ ...current, watermark: DEFAULT_DATAFRAME.watermark }))}>
              <div className="flex flex-wrap items-center gap-1.5">
                <Switch checked={activeDataframe.watermark} label={t('watermark')} onChange={(watermark) => patchActiveDataframe((current) => ({ ...current, watermark }))} />
                <CustomLogoControl />
              </div>
            </Field>
            <Field label={t('copyright')} jsonPath="dataframes[i].copyright" level="default" changed={activeDataframe.copyright !== DEFAULT_DATAFRAME.copyright} onReset={() => patchActiveDataframe((current) => ({ ...current, copyright: DEFAULT_DATAFRAME.copyright }))}>
              <Switch checked={activeDataframe.copyright} label={t('copyright')} onChange={(copyright) => patchActiveDataframe((current) => ({ ...current, copyright }))} />
            </Field>
          </>
        )}
      </div>
    </div>
  )
}
