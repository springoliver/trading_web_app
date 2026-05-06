<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import api, { getAccessToken } from '@/services/api'

const router = useRouter()
const symbol = ref('AAPL')
const optionType = ref('call')
const quantity = ref(1)
const underlyingPrice = ref(null)
const optionInfo = ref({})
const status = ref('Connecting price feed...')
const positions = ref([])
const error = ref('')
const speedResult = ref(null)
let ws = null
let positionsTimer = null

const connectPriceFeed = () => {
  const token = getAccessToken()
  if (!token) {
    logout()
    return
  }
  if (ws) {
    ws.close()
  }
  status.value = 'Connecting price feed...'
  const wsBase = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/^http/, 'ws')
  const wsUrl = `${wsBase}/ws/${symbol.value}?option_type=${optionType.value}&token=${encodeURIComponent(token)}`
  ws = new WebSocket(wsUrl)
  ws.onopen = () => {
    status.value = 'Live price feed connected'
  }
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.underlying_price) {
      underlyingPrice.value = parseFloat(data.underlying_price)
    }
    if (data.option) {
      optionInfo.value = data.option
    }
  }
  ws.onerror = () => {
    status.value = 'Price feed error. Check backend connection.'
  }
  ws.onclose = (event) => {
    if (event?.code === 1008) {
      logout()
      return
    }
    status.value = 'Price feed disconnected'
  }
}

const loadOption = async () => {
  error.value = ''
  try {
    const response = await api.get('/trade/price', {
      params: {
        symbol: symbol.value,
        option_type: optionType.value,
      },
    })
    optionInfo.value = response.data.option || {}
    underlyingPrice.value = response.data.underlying_price
  } catch (err) {
    error.value = err.response?.data?.detail || 'Unable to load option data.'
  }
}

const loadPositions = async () => {
  error.value = ''
  try {
    const response = await api.get('/trade/positions')
    positions.value = response.data.positions || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Unable to load open positions.'
  }
}

const tradeOption = async (action) => {
  error.value = ''
  const endpoint = action === 'sell' ? '/trade/sell' : '/trade/buy'
  try {
    await api.post(endpoint, {
      symbol: symbol.value,
      option_type: optionType.value,
      quantity: quantity.value,
    })
    await loadPositions()
    await loadOption()
    status.value = `${action.toUpperCase()} ${optionType.value.toUpperCase()} order submitted`
  } catch (err) {
    const defaultMsg = action === 'sell' ? 'Sell order failed.' : 'Buy order failed.'
    error.value = err.response?.data?.detail || defaultMsg
  }
}

const closePosition = async (position) => {
  error.value = ''
  try {
    await api.post('/trade/close', {
      symbol: position.symbol,
      option_type: position.option_type,
      strike: position.strike_price,
      expiration_date: position.expiration_date,
      quantity: position.quantity,
      side: position.side,
      market_price: position.market_price,
    })
    await loadPositions()
    status.value = 'Close request sent'
  } catch (err) {
    error.value = err.response?.data?.detail || 'Close order failed.'
  }
}

const logout = () => {
  localStorage.removeItem('access_token')
  router.push('/login')
}

watch([symbol, optionType], () => {
  loadOption()
  connectPriceFeed()
  runSpeedTest()
})

const runSpeedTest = async () => {
  try {
    const response = await api.get('/trade/speed-test', {
      params: { symbol: symbol.value, option_type: optionType.value },
    })
    speedResult.value = response.data
  } catch {
    speedResult.value = null
  }
}

onMounted(() => {
  loadOption()
  loadPositions()
  connectPriceFeed()
  runSpeedTest()
  positionsTimer = window.setInterval(loadPositions, 1000)
})

onBeforeUnmount(() => {
  if (ws) ws.close()
  if (positionsTimer) window.clearInterval(positionsTimer)
})
</script>

<template>
  <VContainer fluid class="pa-6">
    <VRow class="mb-6">
      <VCol cols="12" class="d-flex justify-space-between align-center">
        <div>
          <h3 class="mb-2">Real-Time Options Trading</h3>
          <p class="mb-0">Trade 1 DTE option strikes with fast buy/sell controls and live price updates.</p>
        </div>
        <VBtn color="error" variant="tonal" @click="logout">Logout</VBtn>
      </VCol>
    </VRow>

    <VRow>
      <VCol cols="12" lg="7">
        <VCard class="pa-4 mb-6">
          <VCardTitle>Symbol & Live Panel</VCardTitle>
          <VCardText>
            <VRow>
              <VCol cols="12" md="4">
                <VTextField v-model="symbol" label="Underlying symbol" />
              </VCol>
              <VCol cols="12" md="4">
                <VSelect
                  v-model="optionType"
                  label="Option type"
                  :items="['call', 'put']"
                />
              </VCol>
              <VCol cols="12" md="4">
                <VTextField v-model="quantity" type="number" label="Contracts" min="1" />
              </VCol>
            </VRow>

            <VRow class="mt-4">
              <VCol cols="12" md="4">
                <VCard class="pa-4" color="surface-2" elevation="1">
                  <div class="text-caption mb-2">Underlying Price</div>
                  <div class="text-h5">{{ underlyingPrice ? `$${underlyingPrice.toFixed(2)}` : '---' }}</div>
                </VCard>
              </VCol>
              <VCol cols="12" md="4">
                <VCard class="pa-4" color="surface-2" elevation="1">
                  <div class="text-caption mb-2">Closest Strike</div>
                  <div class="text-h5">{{ optionInfo.strike_price || '---' }}</div>
                  <div class="text-caption">Exp: {{ optionInfo.expiration_date || '---' }}</div>
                </VCard>
              </VCol>
              <VCol cols="12" md="4">
                <VCard class="pa-4" color="surface-2" elevation="1">
                  <div class="text-caption mb-2">Option Mark</div>
                  <div class="text-h5">{{ optionInfo.mark_price ? `$${optionInfo.mark_price.toFixed(2)}` : '---' }}</div>
                  <div class="text-caption">Type: {{ optionInfo.option_type?.toUpperCase() || '---' }}</div>
                </VCard>
              </VCol>
            </VRow>

            <VRow class="mt-4">
              <VCol cols="12" md="6">
                <VBtn color="success" class="me-4" @click="tradeOption('buy')">BUY</VBtn>
                <VBtn color="error" class="me-4" @click="tradeOption('sell')">SELL</VBtn>
              </VCol>
              <VCol cols="12" md="6" class="d-flex align-center justify-end">
                <span class="text-caption me-2">Status:</span>
                <strong>{{ status }}</strong>
              </VCol>
            </VRow>
            <VRow class="mt-2">
              <VCol cols="12">
                <div class="text-caption">Speed Test (backend quote latency)</div>
                <div v-if="speedResult">
                  <strong>{{ speedResult.server_latency_ms }}ms</strong>
                  <span class="ms-2" :class="speedResult.pass ? 'text-success' : 'text-error'">
                    {{ speedResult.pass ? 'PASS (<250ms)' : 'ABOVE TARGET' }}
                  </span>
                </div>
                <div v-else>Unavailable</div>
              </VCol>
            </VRow>

            <VAlert v-if="error" type="error" class="mt-4">{{ error }}</VAlert>
          </VCardText>
        </VCard>
      </VCol>

      <VCol cols="12" lg="5">
        <VCard class="pa-4 mb-6">
          <VCardTitle>Open Positions</VCardTitle>
          <VCardText>
            <div v-if="!positions.length" class="text-caption">No open option positions found.</div>
            <div v-for="position in positions" :key="`${position.symbol}-${position.strike_price}-${position.expiration_date}`" class="mb-4">
              <VCard class="pa-3" elevation="1">
                <div class="d-flex justify-space-between align-center mb-3">
                  <div>
                    <div class="text-subtitle-2">{{ position.symbol }} {{ position.option_type.toUpperCase() }} • {{ position.side.toUpperCase() }}</div>
                    <div class="text-caption">Strike {{ position.strike_price }} • Exp {{ position.expiration_date }}</div>
                  </div>
                  <VBtn size="small" color="error" variant="tonal" @click="closePosition(position)">❌ Close</VBtn>
                </div>
                <VRow>
                  <VCol cols="6">
                    <div class="text-caption">Qty</div>
                    <div>{{ position.quantity }}</div>
                  </VCol>
                  <VCol cols="6">
                    <div class="text-caption">Mark</div>
                    <div>{{ position.market_price ? `$${position.market_price.toFixed(2)}` : '---' }}</div>
                  </VCol>
                </VRow>
                <VRow class="mt-2">
                  <VCol cols="12">
                    <div class="text-caption">P/L</div>
                    <div>
                      <strong v-if="position.unrealized_pl !== null">{{ position.unrealized_pl >= 0 ? '+' : '' }}${{ position.unrealized_pl.toFixed(2) }}</strong>
                      <span v-else>--</span>
                    </div>
                  </VCol>
                </VRow>
              </VCard>
            </div>
          </VCardText>
        </VCard>
      </VCol>
    </VRow>
  </VContainer>
</template>

<style scoped>
.text-caption {
  color: rgba(55, 65, 81, 0.8);
}
</style>

<route lang="yaml">
meta:
  requiresAuth: true
</route>
