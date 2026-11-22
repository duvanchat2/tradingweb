from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_navigation_swap_and_stake_interactions_are_present():
    shell = (ROOT / 'apps/web/components/PanelShell.tsx').read_text(encoding='utf-8')
    page = ''.join((ROOT / path).read_text(encoding='utf-8') for path in (
        'apps/web/app/(panel)/[...section]/page.tsx',
        'apps/web/components/SwapRequestForm.tsx',
        'apps/web/components/StakeWorkspace.tsx',
    ))
    assert 'activePanelSection' in shell
    for label in ('25%', '50%', '75%', 'Máx'):
        assert label in page
    assert 'stake-tabs' in page
    assert 'Mis CDT' in page
